"""Football Elo ratings over the real chronological match history.

Why Elo *alongside* the Bayesian model
--------------------------------------
The Bayesian model pools all matches in a window and estimates a strength with
uncertainty — great for "how good is this team, and how sure are we?" Elo is
**sequential**: it walks matches in date order and nudges each team's rating
after every game, weighting recent and high-stakes games more. That makes it the
natural answer to "who is hot *right now*, respecting the latest results" — a
World Cup win moves the needle far more than an old friendly.

The update (World Football Elo style)
-------------------------------------
For a match, each side's expected result is a logistic of the rating gap::

    E_home = 1 / (1 + 10 ** (-(R_home + HFA - R_away) / 400))

Ratings update toward the actual result, scaled by match importance ``K`` and a
goal-difference multiplier ``G``::

    R' = R + K * G * (W - E)          W = 1 (win) / 0.5 (draw) / 0 (loss)

* ``K`` is larger for World Cups than friendlies — recent competitive games
  dominate, exactly the "current results" emphasis the brief asked for.
* ``G`` grows (sub-linearly) with margin of victory, so blowouts move more.
* ``HFA`` (home-field advantage) is applied unless the match is at a neutral
  venue (World Cup games are neutral except for host nations).
"""

from __future__ import annotations

import math

import pandas as pd

from ..data.teams import HOSTS, TEAMS

# Match-importance K by tournament keyword (checked as substrings, case-insensitive).
K_BY_TOURNAMENT = [
    ("fifa world cup", 60),
    ("world cup qualification", 40),
    ("uefa euro", 50), ("copa am", 50), ("african cup", 50), ("afc asian cup", 50),
    ("nations league", 35),
    ("confederations", 45),
    ("friendly", 20),
]
K_DEFAULT = 30
HFA = 65.0          # home-field advantage in rating points
BASE_RATING = 1500.0


def _k_for(tournament: str) -> int:
    t = str(tournament).lower()
    for key, k in K_BY_TOURNAMENT:
        if key in t:
            return k
    return K_DEFAULT


def _g_multiplier(goal_diff: int) -> float:
    """Goal-difference weighting (World Football Elo formula)."""
    gd = abs(goal_diff)
    if gd <= 1:
        return 1.0
    if gd == 2:
        return 1.5
    return (11 + gd) / 8.0


def _step(ratings: dict, games: dict, m, hfa: float) -> None:
    """Apply one match's Elo update in place (shared by run_elo + backtest)."""
    h, a = m.home_team, m.away_team
    neutral = bool(getattr(m, "neutral", True))
    adj = 0.0 if neutral else hfa
    rh, ra = ratings.get(h, BASE_RATING), ratings.get(a, BASE_RATING)
    e_home = 1.0 / (1.0 + 10 ** (-(rh + adj - ra) / 400.0))

    gh, ga = int(m.home_goals), int(m.away_goals)
    w_home = 1.0 if gh > ga else 0.0 if gh < ga else 0.5
    k = _k_for(getattr(m, "tournament", "")) * _g_multiplier(gh - ga)
    delta = k * (w_home - e_home)
    ratings[h] = rh + delta
    ratings[a] = ra - delta
    games[h] = games.get(h, 0) + 1
    games[a] = games.get(a, 0) + 1


def run_elo(matches: pd.DataFrame, hfa: float = HFA) -> pd.DataFrame:
    """Walk matches in date order; return final ratings for our 48 teams.

    ``matches`` needs columns: date, home_team, away_team, home_goals,
    away_goals, tournament, neutral. Teams unseen default to BASE_RATING.
    """
    ratings: dict[str, float] = {}
    games: dict[str, int] = {}
    df = matches.sort_values("date") if "date" in matches.columns else matches
    for m in df.itertuples():
        _step(ratings, games, m, hfa)

    rows = [{"team": t.name, "elo": round(ratings.get(t.name, BASE_RATING), 1),
             "games": games.get(t.name, 0)} for t in TEAMS]
    out = pd.DataFrame(rows).sort_values("elo", ascending=False).reset_index(drop=True)
    out["rank"] = range(1, len(out) + 1)
    return out


def _elo_1x2(rh: float, ra: float, neutral: bool, hfa: float) -> tuple[float, float, float]:
    """1X2 from an Elo gap; draw mass peaks for evenly-matched sides."""
    adj = 0.0 if neutral else hfa
    p_home_raw = 1.0 / (1.0 + 10 ** (-(rh + adj - ra) / 400.0))
    draw = 0.10 + 0.22 * (1 - abs(p_home_raw - 0.5) * 2)
    return p_home_raw * (1 - draw), draw, (1 - p_home_raw) * (1 - draw)


def rolling_backtest(history: pd.DataFrame, targets: pd.DataFrame,
                     hfa: float = HFA) -> pd.DataFrame:
    """Out-of-sample predicted-vs-true track.

    Seed Elo on ``history``, then walk ``targets`` in date order: predict each
    match from PRE-match ratings (never seeing the result first), record the
    predicted vs actual winner, THEN update with the real score. Returns a
    DataFrame: date, home, away, p_home/p_draw/p_away, pred, actual, hit.
    """
    ratings: dict[str, float] = {}
    games: dict[str, int] = {}
    if "date" in history.columns:
        history = history.sort_values("date")
    for m in history.itertuples():
        _step(ratings, games, m, hfa)

    tg = targets.sort_values("date") if "date" in targets.columns else targets
    rows = []
    for m in tg.itertuples():
        h, a = m.home_team, m.away_team
        neutral = bool(getattr(m, "neutral", True))
        rh, ra = ratings.get(h, BASE_RATING), ratings.get(a, BASE_RATING)
        pH, pD, pA = _elo_1x2(rh, ra, neutral, hfa)
        gh, ga = int(m.home_goals), int(m.away_goals)
        actual = h if gh > ga else a if ga > gh else "Draw"
        pred = max([(h, pH), ("Draw", pD), (a, pA)], key=lambda t: t[1])[0]
        rows.append({"date": str(getattr(m, "date", "")).split()[0],
                     "home": h, "away": a, "score": f"{gh}-{ga}",
                     "p_home": round(pH, 3), "p_draw": round(pD, 3),
                     "p_away": round(pA, 3), "pred": pred, "actual": actual,
                     "hit": pred == actual})
        _step(ratings, games, m, hfa)
    return pd.DataFrame(rows)


def win_probability(elo_a: float, elo_b: float, neutral: bool = True) -> float:
    """P(team A beats team B) from their Elo gap (draws split evenly)."""
    adj = 0.0 if neutral else HFA
    return 1.0 / (1.0 + 10 ** (-(elo_a + adj - elo_b) / 400.0))


def elo_lookup(elo_table: pd.DataFrame) -> dict[str, float]:
    return dict(zip(elo_table["team"], elo_table["elo"]))


def is_host(team: str) -> bool:
    return team in HOSTS
