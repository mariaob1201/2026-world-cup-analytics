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

    from wc2026.features.tactics import matchup_tactics
    teams = generate_players()["team"].unique()
    mt = matchup_tactics(generate_players()[generate_players()["team"] == teams[0]],
                         generate_players()[generate_players()["team"] == teams[1]])
    assert len(mt["line_battles"]) == 3 and "verdict" in mt


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


def test_llm_judge_fallback(monkeypatch):
    """Judge falls back to Elo (no provider key) and returns coherent 1X2 probs."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
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


def test_momentum():
    """Form shifts are bounded; a recent winner gets a positive nudge."""
    import pandas as pd

    from wc2026.models.momentum import MAX_SHIFT, combined_shifts, form_shifts

    m = pd.DataFrame({
        "date": ["2026-05-01", "2026-05-10", "2026-06-01"],
        "home_team": ["Argentina", "Argentina", "Haiti"],
        "away_team": ["Haiti", "Haiti", "Argentina"],
        "home_goals": [4, 3, 0], "away_goals": [0, 0, 2],
    })
    s = form_shifts(m, asof="2026-06-19")
    assert all(abs(v) <= MAX_SHIFT + 1e-9 for v in s.values())
    assert s["Argentina"] > s["Haiti"]   # winners nudged up relative to losers

    c = combined_shifts(m, "2026-06-19", scouted={"Mexico": "leaning positive"})
    assert c["Mexico"] > 0               # positive sentiment adds a small nudge

    # performance_form: a side creating more xG than it concedes is nudged up.
    from wc2026.models.momentum import MAX_SHIFT, performance_form
    stats = pd.DataFrame({
        "date": ["2026-05-01", "2026-05-10", "2026-06-01"],
        "home_team": ["Brazil", "Brazil", "Panama"],
        "away_team": ["Panama", "Panama", "Brazil"],
        "home_xg": [2.5, 2.0, 0.4], "away_xg": [0.5, 0.6, 2.3],
    })
    pf = performance_form(stats, asof="2026-06-19", metric="xg")
    assert pf["Brazil"] > 0 > pf["Panama"]
    assert all(abs(v) <= MAX_SHIFT + 1e-9 for v in pf.values())


def test_simulation_conditions_on_results():
    """A team handed a fixed group win should out-advance one handed a loss."""
    import numpy as np
    import pandas as pd
    import pymc as pm

    from wc2026.data.teams import TEAMS, by_group
    from wc2026.models.bayesian_score import FitResult, build_model
    from wc2026.models.simulate import simulate_tournament

    teams = [t.name for t in TEAMS]
    matches = generate_matches().head(150)
    with build_model(matches, teams, prior_strength=np.zeros(len(teams))):
        idata = pm.sample(draws=40, tune=40, chains=2, cores=1,
                          progressbar=False, random_seed=3)
    fit = FitResult(idata=idata, teams=teams,
                    team_to_idx={t: i for i, t in enumerate(teams)})
    groups = {g: [t.name for t in ts] for g, ts in by_group().items()}
    fixtures = pd.DataFrame([
        {"group": g, "home_team": m[i], "away_team": m[j]}
        for g, m in groups.items() for i in range(4) for j in range(i + 1, 4)
    ])
    a, b = groups["A"][0], groups["A"][1]
    # Hand team `a` a thumping win over `b` in their group game.
    sim = simulate_tournament(fit, fixtures, groups, n_sims=200,
                              played={(a, b): (4, 0)})
    pa = sim.loc[sim.team == a, "p_round32"].iloc[0]
    pb = sim.loc[sim.team == b, "p_round32"].iloc[0]
    assert pa >= pb   # the fixed winner advances at least as often


def test_age_role_weights():
    """Pace weight falls with age; experience weight rises — the age×role idea."""
    from wc2026.data.live_squads import _experience_weight, _youth_pace_weight

    assert _youth_pace_weight(20) > _youth_pace_weight(30) > _youth_pace_weight(35)
    assert _experience_weight(33) > _experience_weight(28) > _experience_weight(22)
    # bounded
    assert 0.75 <= _youth_pace_weight(40) <= 1.20
    assert 0.80 <= _experience_weight(40) <= 1.25


def test_live_squads_parser():
    """Wikitext squad parser is pure and offline-testable."""
    from wc2026.data.live_squads import parse_squads

    wt = (
        "==Group A==\n"
        "===Mexico===\n"
        "{{nat fs g player|no=1|pos=GK|name=[[Guillermo Ochoa]]|"
        "age={{birth date and age2|2026|6|11|1985|7|13}}|caps=152|goals=0|"
        "club=[[AEL Limassol]]|clubnat=CYP}}\n"
        "{{nat fs g player|no=9|pos=FW|name=[[Raúl Jiménez (footballer)|Raúl Jiménez]]|"
        "age={{birth date and age2|2026|6|11|1991|5|5}}|caps=124|goals=40|"
        "club=[[Fulham F.C.|Fulham]]|clubnat=ENG}}\n"
        "===Notateam===\n"
        "{{nat fs g player|no=1|pos=GK|name=[[Someone]]|caps=1}}\n"
    )
    df = parse_squads(wt)
    assert set(df["team"]) == {"Mexico"}          # non-team header ignored
    j = df[df["name"] == "Raúl Jiménez"].iloc[0]   # disambiguation stripped
    assert j["position"] == "FW" and j["caps"] == 124 and j["age"] == 35


def test_sentiment_feature(monkeypatch):
    """Social-sentiment feature: neutral (0) with no LLM; shifts stay capped."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    from wc2026.features.sentiment import CAP, sentiment_shifts, social_sentiment

    scores = social_sentiment({"Mexico": "fans buzzing after the win",
                               "Brazil": "crisis talk in the press"})
    assert scores["Mexico"] == 0.0 and scores["Brazil"] == 0.0   # no LLM -> neutral
    shifts = sentiment_shifts({"A": 2.0, "B": -2.0, "C": 0.2})  # 2.0*SCALE > CAP
    assert shifts["A"] == CAP and shifts["B"] == -CAP            # cap binds
    assert all(abs(v) <= CAP + 1e-9 for v in shifts.values())


def test_llm_extract_fallback(monkeypatch):
    """Feature extractor returns a neutral stub without an LLM, and maps signal."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    from wc2026.models.llm_extract import extract_features, momentum_from_features

    f = extract_features("Mexico look sharp ahead of the next match.", team="Mexico")
    sig = getattr(f, "momentum_signal", None)
    if sig is None:
        sig = f["momentum_signal"]
    assert sig == 0.0
    assert abs(momentum_from_features(f)) <= 0.10


def test_xg_model_fits_tiny():
    """The xG (Gamma-likelihood) model compiles, samples, and predicts."""
    import numpy as np
    import pandas as pd
    import pymc as pm

    from wc2026.data.teams import TEAMS
    from wc2026.models.bayesian_score import FitResult, build_xg_model, predict_match

    teams = [t.name for t in TEAMS]
    rng = np.random.default_rng(0)
    sub = teams[:6]
    rows = []
    for _ in range(120):
        h, a = rng.choice(sub, 2, replace=False)
        rows.append({"home_team": h, "away_team": a,
                     "home_xg": float(abs(rng.normal(1.4, 0.5))),
                     "away_xg": float(abs(rng.normal(1.1, 0.5)))})
    df = pd.DataFrame(rows)
    with build_xg_model(df, teams, prior_strength=np.zeros(len(teams))):
        idata = pm.sample(draws=40, tune=40, chains=2, cores=1,
                          progressbar=False, random_seed=2)
    fr = FitResult(idata=idata, teams=teams,
                   team_to_idx={t: i for i, t in enumerate(teams)})
    p = predict_match(idata, teams, sub[0], sub[1])
    assert 0 <= p["p_home_win"] <= 1 and p["exp_goals_home"] > 0


def test_recency_weights():
    """Recent matches weigh more; weights mean-normalize to 1."""
    import numpy as np

    from wc2026.models.bayesian_score import recency_weights

    dates = ["2022-01-01", "2024-01-01", "2026-06-01"]
    w = recency_weights(dates, asof="2026-06-19", half_life_days=540)
    assert w[2] > w[1] > w[0]            # newest heaviest
    assert abs(w.mean() - 1.0) < 1e-9    # mean-normalized


def test_metrics():
    """Proper scoring rules behave: confident-correct beats confident-wrong."""
    from wc2026.models.metrics import evaluate, log_loss, predicted_result, rps

    # RPS: a confident correct call scores better (lower) than a confident wrong one.
    assert rps(0.8, 0.1, 0.1, "H") < rps(0.8, 0.1, 0.1, "A")
    # RPS is ordinal: predicting Home when it was Draw beats predicting Home when Away.
    assert rps(0.8, 0.1, 0.1, "D") < rps(0.8, 0.1, 0.1, "A")
    assert log_loss(0.9, 0.05, 0.05, "H") < log_loss(0.2, 0.4, 0.4, "H")
    assert predicted_result(0.2, 0.3, 0.5) == "A"

    rows = [{"p_H": 0.6, "p_D": 0.25, "p_A": 0.15, "result": "H",
             "pred_total": 2.1, "actual_total": 3}]
    m = evaluate(rows)
    assert m["n"] == 1 and 0 <= m["RPS"] <= 1 and m["goals_MAE"] == 0.9


def test_abc_recovers_truth():
    """Rejection-ABC (likelihood-free) recovers the home advantage it generated."""
    import numpy as np

    from wc2026.models.abc import (TRUE_HOME_ADV, TRUE_INTERCEPT, TRUE_STR,
                                   abc_infer, fixtures, simulate, summary)
    rng = np.random.default_rng(0)
    hi, ai = fixtures(250, rng)
    gh, ga = simulate(TRUE_STR, TRUE_HOME_ADV, TRUE_INTERCEPT, hi, ai, rng)
    post = abc_infer(summary(gh, ga, hi, ai), hi, ai, n_sims=3000, seed=1)
    assert abs(post["home_adv"].mean() - TRUE_HOME_ADV) < 0.15
    assert post["str_T0"].mean() > post["str_T5"].mean()   # strong > weak


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


def test_winners_elo_goals_and_sim():
    """Stage 28: Elo goals model + state-conditioned champion simulation."""
    import importlib.util
    from pathlib import Path

    spec = importlib.util.spec_from_file_location(
        "predict_winners", Path(__file__).parent.parent / "scripts" / "28_predict_winners.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    # Stronger Elo -> higher scoring rate and higher win probability.
    la, lb = mod.elo_goals(1800, 1500, neutral=True)
    assert la > lb > 0
    p = mod.poisson_1x2(la, lb)
    assert p["p_a"] > p["p_b"]
    assert abs(p["p_a"] + p["p_draw"] + p["p_b"] - 1.0) < 1e-2  # 8-goal truncation

    # Tiny champion sim over two groups; probabilities are well-formed.
    groups = {"A": ["T0", "T1", "T2", "T3"], "B": ["T4", "T5", "T6", "T7"]}
    elo = {f"T{i}": 1500 + (8 - i) * 40 for i in range(8)}
    sc = mod.simulate_champion(elo, groups, played={}, n_sims=200)
    assert len(sc) == 8
    assert abs(sc["p_champion"].sum() - 1.0) < 1e-6
    assert (sc["p_round16"] <= 1.0).all() and (sc["p_round16"] >= 0.0).all()
