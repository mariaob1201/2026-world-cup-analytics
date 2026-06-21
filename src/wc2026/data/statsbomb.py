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
        acc = {home: dict(xg=0.0, shots=0, sot=0, passes=0),
               away: dict(xg=0.0, shots=0, sot=0, passes=0)}
        for e in events:
            t = e.get("team", {}).get("name")
            if t not in acc:
                continue
            typ = e.get("type", {}).get("name")
            if typ == "Shot":
                shot = e.get("shot", {})
                acc[t]["xg"] += shot.get("statsbomb_xg", 0.0) or 0.0
                acc[t]["shots"] += 1
                if shot.get("outcome", {}).get("name") in _ON_TARGET:
                    acc[t]["sot"] += 1
            elif typ == "Pass":
                acc[t]["passes"] += 1
        tot_pass = acc[home]["passes"] + acc[away]["passes"] or 1
        rows.append({
            "date": m["match_date"], "home_team": home, "away_team": away,
            "home_goals": int(m["home_score"]), "away_goals": int(m["away_score"]),
            "home_xg": round(acc[home]["xg"], 3), "away_xg": round(acc[away]["xg"], 3),
            "home_shots": acc[home]["shots"], "away_shots": acc[away]["shots"],
            "home_sot": acc[home]["sot"], "away_sot": acc[away]["sot"],
            "home_poss": round(acc[home]["passes"] / tot_pass, 3),
            "away_poss": round(acc[away]["passes"] / tot_pass, 3),
        })
    return pd.DataFrame(rows).sort_values("date").reset_index(drop=True)
