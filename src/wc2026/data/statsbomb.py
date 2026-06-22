"""StatsBomb open-data loader: real per-match xG for past World Cups.

StatsBomb publishes free event-level data (every shot carries ``statsbomb_xg``)
for the 2018 and 2022 men's World Cups — a clean JSON source (no scraping/browser)
to get the xG the xG-model needs. We sum shot xG per team per match to get
``home_xg`` / ``away_xg`` alongside the real goals.

This is what lets the xG-vs-goals backtest (stage 21) run on real data.
"""

from __future__ import annotations

import json
import urllib.request

import pandas as pd

BASE = "https://raw.githubusercontent.com/statsbomb/open-data/master/data"
_UA = "wc2026-analytics/0.1 (research) python-urllib"
# competition 43 = FIFA World Cup; season ids from competitions.json.
WORLD_CUPS = {2018: 3, 2022: 106}


def _get(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": _UA})
    with urllib.request.urlopen(req, timeout=60) as r:  # noqa: S310
        return json.loads(r.read().decode("utf-8"))


# Shot outcomes that count as "on target".
_ON_TARGET = {"Goal", "Saved", "Saved to Post"}

# Defensive-action event types (for pressing/territory).
_DEF_ACTIONS = {"Pressure", "Interception", "Ball Recovery", "Block",
                "Clearance", "Duel", "Foul Committed"}
import math  # noqa: E402


def team_spatial_profiles(year: int) -> "pd.DataFrame":
    """Per-team SPATIAL style from StatsBomb x,y event locations (a WC year).

    The pitch is 120x80, goal at (120, 40). Per team, averaged over its matches:

    * ``shot_dist``    — mean distance of its shots from goal (lower = better
      locations / works the ball into dangerous areas).
    * ``box_share``    — share of its shots taken inside the penalty box.
    * ``territory``    — mean x of its passes/carries (higher = plays more
      advanced; territorial dominance).
    * ``press_height`` — share of its defensive actions in the attacking half
      (higher = high press).

    This is the "spatial analysis" spice: *where* and *how* a team plays, not just
    how much. Feed as covariates / a style layer — and validate on the scoreboard.
    """
    season = WORLD_CUPS[year]
    matches = _get(f"{BASE}/matches/43/{season}.json")
    from collections import defaultdict
    sd = defaultdict(float); shots = defaultdict(int); box = defaultdict(int)
    terr = defaultdict(float); terrn = defaultdict(int)
    press = defaultdict(int); defn = defaultdict(int); games = defaultdict(set)

    for m in matches:
        for e in _get(f"{BASE}/events/{m['match_id']}.json"):
            t = e.get("team", {}).get("name")
            loc = e.get("location")
            typ = e.get("type", {}).get("name")
            if not t or not loc:
                continue
            x, y = loc[0], loc[1]
            games[t].add(m["match_id"])
            if typ == "Shot":
                sd[t] += math.hypot(120 - x, 40 - y); shots[t] += 1
                if x >= 102 and 18 <= y <= 62:
                    box[t] += 1
            elif typ in ("Pass", "Carry"):
                terr[t] += x; terrn[t] += 1
            elif typ in _DEF_ACTIONS:
                defn[t] += 1
                if x > 60:
                    press[t] += 1

    rows = []
    for t in games:
        if shots[t] and terrn[t] and defn[t]:
            rows.append({
                "team": t, "matches": len(games[t]),
                "shot_dist": round(sd[t] / shots[t], 1),
                "box_share": round(box[t] / shots[t], 3),
                "territory": round(terr[t] / terrn[t], 1),
                "press_height": round(press[t] / defn[t], 3),
            })
    return pd.DataFrame(rows).sort_values("territory", ascending=False).reset_index(drop=True)


def fetch_world_cup_xg(year: int) -> pd.DataFrame:
    """Per-match team stats for a World Cup year (2018 or 2022).

    Columns per side: goals, **xg, shots, sot** (shots on target), and **poss**
    (possession proxy = share of passes). These are the high-signal dynamics the
    performance-form conditioner uses (try metric=xg | shots | sot | poss).
    """
    season = WORLD_CUPS[year]
    matches = _get(f"{BASE}/matches/43/{season}.json")
    rows = []
    for m in matches:
        home = m["home_team"]["home_team_name"]
        away = m["away_team"]["away_team_name"]
        events = _get(f"{BASE}/events/{m['match_id']}.json")
        z = lambda: dict(xg=0.0, shots=0, sot=0, passes=0, terr=0.0, terrn=0,
                         defacts=0, press=0)
        acc = {home: z(), away: z()}
        for e in events:
            t = e.get("team", {}).get("name")
            if t not in acc:
                continue
            typ = e.get("type", {}).get("name")
            loc = e.get("location")
            if typ == "Shot":
                shot = e.get("shot", {})
                acc[t]["xg"] += shot.get("statsbomb_xg", 0.0) or 0.0
                acc[t]["shots"] += 1
                if shot.get("outcome", {}).get("name") in _ON_TARGET:
                    acc[t]["sot"] += 1
            elif typ in ("Pass", "Carry"):
                if typ == "Pass":
                    acc[t]["passes"] += 1
                if loc:
                    acc[t]["terr"] += loc[0]; acc[t]["terrn"] += 1
            elif typ in _DEF_ACTIONS and loc:
                acc[t]["defacts"] += 1
                if loc[0] > 60:
                    acc[t]["press"] += 1
        tot_pass = acc[home]["passes"] + acc[away]["passes"] or 1
        row = {"date": m["match_date"], "home_team": home, "away_team": away,
               "home_goals": int(m["home_score"]), "away_goals": int(m["away_score"])}
        for side, t in (("home", home), ("away", away)):
            a = acc[t]
            row[f"{side}_xg"] = round(a["xg"], 3)
            row[f"{side}_shots"] = a["shots"]
            row[f"{side}_sot"] = a["sot"]
            row[f"{side}_poss"] = round(a["passes"] / tot_pass, 3)
            row[f"{side}_territory"] = round(a["terr"] / (a["terrn"] or 1), 2)
            row[f"{side}_press"] = round(a["press"] / (a["defacts"] or 1), 3)
        rows.append(row)
    return pd.DataFrame(rows).sort_values("date").reset_index(drop=True)
