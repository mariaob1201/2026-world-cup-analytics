"""Real 2026 World Cup squads, scraped from Wikipedia.

Fixes the FIFA-dataset vintage problem (retired names like C. Vela). Wikipedia's
"2026 FIFA World Cup squads" page carries the OFFICIAL call-ups in a structured
wikitext template, giving — for every actually-selected player — name, position,
**real age** and **real caps** (true seniority/longevity the FIFA snapshot lacked).

What this does and doesn't give
-------------------------------
* Gives: real roster (name, GK/DF/MF/FW), age (as of kickoff), caps, club.
* Does NOT give: skill ratings (pace/shooting/…). To attach those, join a CURRENT
  EA FC dataset by name (see ``merge_skills`` hook). Until then, use this as the
  source of truth for *who plays* + seniority, and treat FIFA skills as optional.

Parsing is offline-testable: ``parse_squads(wikitext)`` is pure; ``fetch_squads``
just downloads the page first.
"""

from __future__ import annotations

import re
import urllib.request

import pandas as pd

from .teams import TEAMS

SQUADS_URL = "https://en.wikipedia.org/wiki/2026_FIFA_World_Cup_squads?action=raw"

# Wikipedia country header -> our canonical team name.
WIKI_TEAM_ALIASES = {
    "Czech Republic": "Czechia",
    "Turkey": "Türkiye",
    "Bosnia and Herzegovina": "Bosnia-Herzegovina",
    "DR Congo": "Congo DR",
}

_HEADER = re.compile(r"^===\s*([^=]+?)\s*===\s*$")
_PLAYER_PREFIX = "{{nat fs g player|"
_BIRTH = re.compile(r"birth date and age2\|(\d+)\|(\d+)\|(\d+)\|(\d+)\|(\d+)\|(\d+)")


def _field(body: str, key: str) -> str | None:
    m = re.search(rf"\|\s*{key}=([^|}}]*)", body)
    return m.group(1).strip() if m else None


def _clean_link(text: str | None) -> str:
    """[[Target|Display]] or [[Name]] -> human name, sans disambiguation."""
    if not text:
        return ""
    inner = re.sub(r"\[\[|\]\]", "", text).split("|")[-1].strip()
    return re.sub(r"\s*\([^)]*\)\s*$", "", inner).strip()  # drop "(footballer)" etc.


def parse_squads(wikitext: str) -> pd.DataFrame:
    """Parse the squads wikitext into one row per selected player."""
    valid = {t.name for t in TEAMS}
    rows: list[dict] = []
    current: str | None = None

    for line in wikitext.splitlines():
        h = _HEADER.match(line.strip())
        if h:
            name = h.group(1).strip()
            canon = WIKI_TEAM_ALIASES.get(name, name)
            current = canon if canon in valid else None
            continue
        if current is None or _PLAYER_PREFIX not in line:
            continue
        # The player template contains a nested {{birth...}} template, so match
        # the whole line rather than a non-greedy {{...}} (which stops early).
        body = "|" + line.split(_PLAYER_PREFIX, 1)[1]
        age = None
        b = _BIRTH.search(body)
        if b:
            ref_y, ref_m, ref_d, by, bm, bd = map(int, b.groups())
            age = ref_y - by - ((ref_m, ref_d) < (bm, bd))
        rows.append({
            "team": current,
            "name": _clean_link(_field(body, "name")),
            "position": (_field(body, "pos") or "").upper(),
            "age": age,
            "caps": int(_field(body, "caps") or 0),
            "club": _clean_link(_field(body, "club")),
        })
    return pd.DataFrame(rows)


# Wikipedia rejects requests without a descriptive User-Agent (HTTP 403).
_UA = "wc2026-analytics/0.1 (https://github.com/; research) python-urllib"


def fetch_squads(force: bool = False) -> pd.DataFrame:
    """Download + parse the live squads page."""
    req = urllib.request.Request(SQUADS_URL, headers={"User-Agent": _UA})
    with urllib.request.urlopen(req, timeout=30) as r:  # noqa: S310
        wikitext = r.read().decode("utf-8")
    return parse_squads(wikitext)


def _youth_pace_weight(age):
    """Pace peaks young and declines with age — so young attackers' pace counts
    more (speed threat). ~1.2 at 20, ~1.0 at 30, ~0.85 at 35."""
    import numpy as np
    return np.clip(1.20 - np.maximum(0, age - 23) * 0.03, 0.75, 1.20)


def _experience_weight(age):
    """Defensive reading / ball retention improves with experience — so senior
    defenders' solidity counts more. ~0.8 at 22, ~1.0 at 30, capped ~1.25."""
    import numpy as np
    return np.clip(0.80 + np.maximum(0, age - 22) * 0.025, 0.80, 1.25)


def live_team_features(live: pd.DataFrame, fifa: pd.DataFrame) -> pd.DataFrame:
    """Per-team prior from the REAL roster + skill join + an AGE×ROLE signal.

    Roster, position, age and caps are REAL (Wikipedia). Skills (overall, pace,
    defending) are joined from FIFA by last name (team-median fill for unmatched).
    On top of overall quality, an **age×role×skill** term encodes:

    * **young pace in attack** — attackers' pace weighted up for younger players
      (speed peaks young);
    * **senior solidity in defence** — defenders' defending weighted up for older
      players (positioning / ball retention improve with experience).

    Both fold into `prior_strength` with a small weight (the model's `beta_prior`
    still learns how much to trust the prior overall). Columns: squad_overall,
    avg_caps, avg_age, young_pace, senior_solidity, age_role, prior_strength.
    """
    import numpy as np

    def last(n):
        return str(n).split()[-1].lower()

    cols = ["short_name", "overall", "pace", "defending"]
    rt = fifa[cols].copy()
    rt["_last"] = rt["short_name"].map(last)
    rt = rt.sort_values("overall", ascending=False).drop_duplicates("_last")
    m = live.copy()
    m["_last"] = m["name"].map(last)
    m = m.merge(rt[["_last", "overall", "pace", "defending"]], on="_last", how="left")

    # Fill missing skills with each team's median (else global). GKs lack
    # pace/defending in FIFA -> same fill.
    for c in ("overall", "pace", "defending"):
        gmed = m[c].median()
        m[c] = m.groupby("team")[c].transform(lambda s: s.fillna(s.median())).fillna(gmed)

    m["pace_w"] = m["pace"] * _youth_pace_weight(m["age"])
    m["def_w"] = m["defending"] * _experience_weight(m["age"])

    def z(s):
        sd = s.std(ddof=0)
        return (s - s.mean()) / sd if sd else s * 0.0

    rows = []
    for team, g in m.groupby("team"):
        core = g.nlargest(16, "overall")
        att = g[g["position"].isin(["FW", "MF"])]
        deff = g[g["position"] == "DF"]
        rows.append({
            "team": team,
            "squad_overall": round(core["overall"].mean(), 1),
            "avg_caps": round(g["caps"].mean(), 1),
            "avg_age": round(g["age"].mean(), 1),
            # young pace in attack; senior solidity in defence
            "young_pace": round(att["pace_w"].mean(), 1) if len(att) else np.nan,
            "senior_solidity": round(deff["def_w"].mean(), 1) if len(deff) else np.nan,
        })
    tf = pd.DataFrame(rows)
    tf["young_pace"] = tf["young_pace"].fillna(tf["young_pace"].mean())
    tf["senior_solidity"] = tf["senior_solidity"].fillna(tf["senior_solidity"].mean())
    tf["age_role"] = (0.5 * z(tf["young_pace"]) + 0.5 * z(tf["senior_solidity"])).round(3)

    # Skill dominates; caps/age nudge; the age×role term adds a small,
    # role-aware adjustment (validate its weight on the EVALUATION scoreboard).
    composite = (0.80 * z(tf["squad_overall"])
                 + 0.06 * z(np.log1p(tf["avg_caps"]))
                 + 0.04 * z(tf["avg_age"])
                 + 0.10 * z(tf["age_role"]))
    tf["prior_strength"] = (z(composite) * 0.5).round(4)
    return tf.sort_values("prior_strength", ascending=False).reset_index(drop=True)


def merge_skills(squads: pd.DataFrame, ratings: pd.DataFrame,
                 name_col: str = "short_name") -> pd.DataFrame:
    """Attach skill ratings to the real roster by fuzzy last-name match.

    ``ratings`` is any current EA-FC-style table with a name column and skill
    columns. Unmatched players keep NaN skills (fill from position/age priors).
    This is the hook for a CURRENT ratings source; left as an explicit join so
    you can drop in FC24/FC25 without touching the roster.
    """
    def last(n: str) -> str:
        return str(n).split()[-1].lower()

    rt = ratings.copy()
    rt["_last"] = rt[name_col].map(last)
    sq = squads.copy()
    sq["_last"] = sq["name"].map(last)
    return sq.merge(rt.drop_duplicates("_last"), on="_last", how="left").drop(columns="_last")
