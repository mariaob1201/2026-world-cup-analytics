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
