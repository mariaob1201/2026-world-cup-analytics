"""Fast smoke tests: data shapes, features, and a tiny end-to-end model fit.

These run in seconds (a deliberately tiny sampler) so CI can catch breakage
without waiting for a full inference run.
"""

import numpy as np

from wc2026.data.generate_synthetic import (
    generate_fixtures,
    generate_matches,
    generate_players,
)
from wc2026.data.teams import TEAMS, by_group
from wc2026.features.player_features import add_player_features, build_team_features


def test_team_structure():
    assert len(TEAMS) == 48
    assert all(len(v) == 4 for v in by_group().values())


def test_synthetic_shapes():
    players = generate_players()
    assert len(players) == 48 * 26
    assert players["followers"].min() > 0

    fixtures = generate_fixtures()
    assert len(fixtures) == 12 * 6  # 6 games per group

    matches = generate_matches()
    assert {"home_team", "away_team", "home_goals", "away_goals"} <= set(matches.columns)
    assert (matches["home_goals"] >= 0).all()


def test_features():
    players = generate_players()
    feat = add_player_features(players)
    for col in ["longevity", "skill_index", "social_score"]:
        assert col in feat.columns
    team = build_team_features(feat)
    assert len(team) == 48
    assert np.isfinite(team["prior_strength"]).all()


def test_interpretation():
    """Semantic layer runs on synthetic players and emits sane labels."""
    from wc2026.features.interpretation import (
        add_player_interpretation,
        interpret_all_teams,
        team_profiles_markdown,
    )

    players = add_player_features(generate_players())
    roles = add_player_interpretation(players)
    assert roles["role"].notna().all()

    interp = interpret_all_teams(players)
    assert len(interp) == 48
    assert set(interp["tier"]).issubset({
        "Elite contender", "Strong side", "Solid outfit", "Developing team"})
    assert {"style", "depth", "age_profile", "narrative"} <= set(interp.columns)

    md = team_profiles_markdown(interp, players)
    assert md.startswith("#") and "avg top-16 rating" in md


def test_sources_helpers():
    """Position bucketing + proxies are pure and don't need the network."""
    import pandas as pd

    from wc2026.data.sources import _longevity_proxies, _primary_position, _social_proxy

    assert _primary_position("GK") == "GK"
    assert _primary_position("RW, ST, CF") == "FW"
    assert _primary_position("CB, RB") == "DF"
    assert _primary_position("CDM, CM") == "MF"

    age = pd.Series([22, 30, 35])
    rep = pd.Series([1, 3, 5])
    cy, caps, debut = _longevity_proxies(age, rep)
    assert (caps >= 1).all() and (caps <= 180).all()
    foll, eng = _social_proxy(rep, pd.Series([70, 85, 90]))
    assert (foll > 0).all() and (eng.between(0.002, 0.12)).all()


def test_tactics():
    """Formation fit + interpretation run on a synthetic squad."""
    from wc2026.features.tactics import FORMATIONS, formation_fit, interpret_formation

    squad = generate_players()
    squad = squad[squad["team"] == squad["team"].iloc[0]]
    fit = formation_fit(squad)
    assert len(fit) == len(FORMATIONS)
    assert fit["xi_rating"].is_monotonic_decreasing  # sorted best-first

    res = interpret_formation(squad, actual="4-1-4-1")
    assert res["best_formation"] in FORMATIONS
    assert "actual_commentary" in res
    assert res["strongest_line"] in {"defence", "midfield", "attack"}


def test_x_collector_pure_helpers():
    """Sentiment + cost + summary work WITHOUT tweepy or a network."""
    from wc2026.data import x_collector as xc

    assert xc.score_text("Mexico win, what a brilliant clean sheet!") > 0
    assert xc.score_text("awful, boring, lucky and overrated") < 0
    assert xc.score_text("Mexico plays South Korea tonight") == 0

    # 50 posts + 1 user read at pay-per-use rates.
    assert xc.estimate_cost(50, n_users=1) == round(50 * 0.005 + 0.010, 4)

    fake = [
        {"text": "what a win, brilliant and solid!", "like_count": 9},
        {"text": "proud, amazing, deserved", "like_count": 5},
        {"text": "boring, lucky, awful", "like_count": 3},
        {"text": "Mexico vs South Korea today", "like_count": 1},
    ]
    s = xc.summarize_for_scouting(fake)
    assert s["n"] == 4 and s["pos"] == 2 and s["neg"] == 1 and s["neutral"] == 1
    assert s["net_mood"] in {"strongly positive", "leaning positive", "mixed",
                             "leaning negative", "strongly negative"}
    assert xc.summarize_for_scouting([])["n"] == 0


def test_team_structure_real_draw():
    from wc2026.data.teams import by_group
    # Spot-check the real 2026 draw made it in.
    groups = by_group()
    names = {t.name for g in groups.values() for t in g}
    assert {"Mexico", "Czechia", "Senegal", "Curaçao", "Congo DR"} <= names
    a = {t.name for t in groups["A"]}
    assert a == {"Mexico", "South Africa", "South Korea", "Czechia"}


def test_elo():
    import pandas as pd

    from wc2026.models.elo import _g_multiplier, _k_for, run_elo, win_probability

    assert _k_for("FIFA World Cup") > _k_for("Friendly")
    assert _g_multiplier(5) > _g_multiplier(1) == 1.0
    assert 0.5 < win_probability(1700, 1500) < 1.0      # stronger team favoured
    assert abs(win_probability(1500, 1500) - 0.5) < 1e-9

    matches = pd.DataFrame({
        "date": ["2024-01-01", "2024-06-01"],
        "home_team": ["Mexico", "Brazil"], "away_team": ["Brazil", "Mexico"],
        "home_goals": [1, 3], "away_goals": [0, 0],
        "tournament": ["Friendly", "FIFA World Cup"], "neutral": [True, True],
    })
    elo = run_elo(matches)
    assert len(elo) == 48 and {"team", "elo", "rank"} <= set(elo.columns)


def test_llm_judge_fallback():
    """Judge falls back to Elo (no SDK/key) and returns coherent 1X2 probs."""
    from wc2026.models.llm_judge import Fixture, TeamContext, elo_fallback

    fx = Fixture(
        a=TeamContext("Mexico", elo=1604, elo_rank=7),
        b=TeamContext("Senegal", elo=1483, elo_rank=20),
        stage="Round of 32", venue="Estadio Azteca (Mexico home)",
    )
    v = elo_fallback(fx)
    total = v["p_a_win"] + v["p_draw"] + v["p_b_win"]
    assert abs(total - 1.0) < 0.05
    assert v["p_a_win"] > v["p_b_win"]   # higher Elo + home favoured


def test_model_fits_tiny():
    """A minimal NUTS run just to prove the model compiles and samples."""
    import pymc as pm  # imported here so non-model tests don't pay the cost

    from wc2026.models.bayesian_score import build_model, posterior_strength_table
    from wc2026.models.bayesian_score import FitResult

    matches = generate_matches().head(200)
    teams = [t.name for t in TEAMS]
    model = build_model(matches, teams, prior_strength=np.zeros(len(teams)))
    with model:
        idata = pm.sample(draws=50, tune=50, chains=2, cores=1,
                          progressbar=False, random_seed=1)
    fr = FitResult(idata=idata, teams=teams,
                   team_to_idx={t: i for i, t in enumerate(teams)})
    strength = posterior_strength_table(fr)
    assert len(strength) == 48
