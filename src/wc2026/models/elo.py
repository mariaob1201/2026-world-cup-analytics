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


def run_elo(matches: pd.DataFrame, hfa: float = HFA) -> pd.DataFrame:
    """Walk matches in date order; return final ratings for our 48 teams.

    ``matches`` needs columns: date, home_team, away_team, home_goals,
    away_goals, tournament, neutral. Teams unseen default to BASE_RATING.
    """
    ratings: dict[str, float] = {}
    games: dict[str, int] = {}

    def R(team: str) -> float:
        return ratings.get(team, BASE_RATING)

    df = matches.sort_values("date") if "date" in matches.columns else matches
    for m in df.itertuples():
        h, a = m.home_team, m.away_team
        neutral = bool(getattr(m, "neutral", True))
        adj = 0.0 if neutral else hfa
        e_home = 1.0 / (1.0 + 10 ** (-(R(h) + adj - R(a)) / 400.0))

        gh, ga = int(m.home_goals), int(m.away_goals)
        if gh > ga:
            w_home = 1.0
        elif gh < ga:
            w_home = 0.0
        else:
            w_home = 0.5

        k = _k_for(getattr(m, "tournament", "")) * _g_multiplier(gh - ga)
        delta = k * (w_home - e_home)
        ratings[h] = R(h) + delta
        ratings[a] = R(a) - delta
        games[h] = games.get(h, 0) + 1
        games[a] = games.get(a, 0) + 1

    rows = [{"team": t.name, "elo": round(R(t.name), 1), "games": games.get(t.name, 0)}
            for t in TEAMS]
    out = pd.DataFrame(rows).sort_values("elo", ascending=False).reset_index(drop=True)
    out["rank"] = range(1, len(out) + 1)
    return out


def win_probability(elo_a: float, elo_b: float, neutral: bool = True) -> float:
    """P(team A beats team B) from their Elo gap (draws split evenly)."""
    adj = 0.0 if neutral else HFA
    return 1.0 / (1.0 + 10 ** (-(elo_a + adj - elo_b) / 400.0))


def elo_lookup(elo_table: pd.DataFrame) -> dict[str, float]:
    return dict(zip(elo_table["team"], elo_table["elo"]))


def is_host(team: str) -> bool:
    return team in HOSTS
