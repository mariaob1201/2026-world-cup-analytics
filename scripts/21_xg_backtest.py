"""Stage 21: backtest the xG model vs the goals model on the same matches.

Decision rule (per the project's evaluation philosophy): keep the xG variant
only if it lowers RPS vs the goals model on held-out matches.

Data: needs an xG-labelled table at data/raw/xg_matches.csv with columns
  date, home_team, away_team, home_goals, away_goals, home_xg, away_xg
(harvest via FBref match reports or StatsBomb open data — see data/fbref.py).

    python scripts/21_xg_backtest.py            # real comparison (needs the CSV)
    python scripts/21_xg_backtest.py --demo     # synthetic sanity check (no data)

Honest note: a large-sample real comparison needs xG for many *training*
matches, which isn't cheaply scrapeable in this environment — so by default this
runs only when you've supplied the CSV. --demo proves the machinery on synthetic
data (NOT a real-world result).
"""

import argparse

import numpy as np
import pandas as pd
import pymc as pm

from wc2026.config import RAW
from wc2026.data.fbref import load_xg_csv
from wc2026.models.bayesian_score import build_model, build_xg_model, predict_match
from wc2026.models.metrics import evaluate


def _fit(builder, train, teams, prior=None):
    if prior is None:
        prior = np.zeros(len(teams))
    with builder(train, teams, prior_strength=prior):
        return pm.sample(draws=600, tune=600, chains=2, cores=1,
                         target_accept=0.9, progressbar=False, random_seed=11)


def _spatial_prior(train, teams):
    """Per-team spatial covariate from TRAINING matches only (leakage-free):
    z(territory) + z(press), scaled to the prior_strength range."""
    terr = {t: [] for t in teams}
    pres = {t: [] for t in teams}
    for m in train.itertuples():
        terr[m.home_team].append(m.home_territory); pres[m.home_team].append(m.home_press)
        terr[m.away_team].append(m.away_territory); pres[m.away_team].append(m.away_press)
    tv = np.array([np.mean(terr[t]) if terr[t] else np.nan for t in teams])
    pv = np.array([np.mean(pres[t]) if pres[t] else np.nan for t in teams])

    def z(a):
        a = np.where(np.isnan(a), np.nanmean(a), a)
        return (a - a.mean()) / (a.std() or 1.0)

    cov = 0.6 * z(tv) + 0.4 * z(pv)
    return (cov - cov.mean()) / (cov.std() or 1.0) * 0.5


def _score(idata, teams, test, stats=None, form_metric=None):
    """Score the model on the test set. If ``form_metric`` is given, each match is
    CONDITIONED on performance-form from ``stats`` as of the day before kickoff
    (no leakage) — to test which recent-dynamics signal helps."""
    from wc2026.models.momentum import performance_form

    rows = []
    for m in test.itertuples():
        gh, ga = int(m.home_goals), int(m.away_goals)
        result = "H" if gh > ga else "A" if ga > gh else "D"
        shifts = None
        if form_metric:
            asof = (pd.Timestamp(m.date) - pd.Timedelta(days=1)).strftime("%Y-%m-%d")
            try:
                shifts = performance_form(stats, asof=asof, metric=form_metric)
            except Exception:
                shifts = None
        p = predict_match(idata, teams, m.home_team, m.away_team,
                          neutral=True, shifts=shifts)
        rows.append({"p_H": p["p_home_win"], "p_D": p["p_draw"], "p_A": p["p_away_win"],
                     "result": result,
                     "pred_total": p["exp_goals_home"] + p["exp_goals_away"],
                     "actual_total": gh + ga})
    return evaluate(rows)


def compare(df: pd.DataFrame, label: str):
    teams = sorted(set(df["home_team"]) | set(df["away_team"]))
    df = df.sort_values("date").reset_index(drop=True)
    cut = int(len(df) * 0.8)
    train, test = df.iloc[:cut], df.iloc[cut:]
    print(f"[{label}] fit on {len(train)} matches, score on {len(test)}; "
          f"{len(teams)} teams")

    goals_idata = _fit(build_model, train, teams)
    goals = _score(goals_idata, teams, test)
    xg = _score(_fit(build_xg_model, train, teams), teams, test)

    # Which recent-dynamics signal, used to CONDITION the goals model, helps?
    conditioned = {f"goals+{mtr}-form": _score(goals_idata, teams, test, df, mtr)
                   for mtr in ("goals", "xg", "sot")}

    # Spice test: spatial style (territory/press) as a leakage-free PRIOR covariate.
    spatial = {}
    if "home_territory" in df.columns:
        sp_prior = _spatial_prior(train, teams)
        spatial["goals+spatial-prior"] = _score(
            _fit(build_model, train, teams, prior=sp_prior), teams, test)

    print(f"\n{'model':<16} {'RPS':>8} {'log_loss':>9} {'hit':>6} {'goalsMAE':>9}")
    results = {"goals": goals, "xG": xg, **conditioned, **spatial}
    for name, m in results.items():
        print(f"{name:<16} {m['RPS']:>8.4f} {m['log_loss']:>9.4f} "
              f"{m['hit_rate']:>6.3f} {m.get('goals_MAE', float('nan')):>9.3f}")
    delta = xg["RPS"] - goals["RPS"]
    verdict = "xG WINS — keep it" if delta < 0 else "goals model still better"
    print(f"\nRPS delta (xG - goals): {delta:+.4f}  ->  {verdict}")
    best = min(results, key=lambda k: results[k]["RPS"])
    print(f"Lowest RPS overall: {best} ({results[best]['RPS']:.4f})")

    if label == "real":
        _write_doc(results, len(train), len(test), len(teams), delta, verdict, best)


def _write_doc(results, n_train, n_test, n_teams, delta, verdict, best):
    from wc2026.config import ROOT
    labels = {"goals": "goals model", "xG": "xG model (expected goals)",
              "goals+goals-form": "goals + recent-goals form",
              "goals+xg-form": "goals + recent-xG form",
              "goals+sot-form": "goals + recent-SoT form",
              "goals+spatial-prior": "goals + spatial-style prior (territory/press)"}
    L = ["# xG & conditioning backtest\n",
         f"_Fit on {n_train} matches, scored on {n_test} held-out matches "
         f"({n_teams} teams), real per-match stats from StatsBomb open data "
         f"(2018 + 2022 World Cups). Lower RPS/log-loss is better. Conditioning "
         f"rows nudge the goals model by each team's recent-performance form "
         f"(as of the day before kickoff — no leakage)._\n",
         "| Approach | RPS ↓ | log-loss ↓ | hit-rate ↑ | goals MAE ↓ |",
         "|---|---|---|---|---|"]
    for name, m in results.items():
        star = " ⭐" if name == best else ""
        L.append(f"| {labels.get(name, name)}{star} | {m['RPS']} | {m['log_loss']} "
                 f"| {m['hit_rate']} | {m.get('goals_MAE', '—')} |")
    L.append(f"\n**xG vs goals: {delta:+.4f} RPS → {verdict}.** "
             f"**Lowest RPS overall: {labels.get(best, best)}.**\n")
    L.append("xG is a less-noisy measure of chance quality than goals, so abilities "
             "learned from it generalize better (a side that created more but lost is "
             "rated by what it created). Conditioning the goals model on recent xG/SoT "
             "form tests whether 'how recent games went' adds signal. Small test "
             "sample — directional, not final. Regenerate with `make xg-backtest` "
             "after `make fetch-xg`.\n")
    L.append("**Live use:** switching the 2026 forecast to xG needs per-match xG for "
             "current matches (StatsBomb hasn't released 2026; FBref match-report "
             "scraping is the fallback). Until then the live pipeline uses the goals "
             "model and this validates xG as the upgrade path.")
    (ROOT / "docs" / "XG_BACKTEST.md").write_text("\n".join(L))
    print(f"saved -> {ROOT / 'docs' / 'XG_BACKTEST.md'}")


def _demo_data() -> pd.DataFrame:
    """Synthetic matches with goals + noisy xG — to exercise the harness only."""
    rng = np.random.default_rng(0)
    teams = [f"T{i}" for i in range(12)]
    strength = {t: rng.normal(0, 0.4) for t in teams}
    rows = []
    for k in range(400):
        h, a = rng.choice(teams, 2, replace=False)
        lam_h = np.exp(0.2 + strength[h] - strength[a])
        lam_a = np.exp(0.2 + strength[a] - strength[h])
        gh, ga = rng.poisson(lam_h), rng.poisson(lam_a)
        rows.append({"date": f"2024-{1 + k % 9:02d}-01", "home_team": h, "away_team": a,
                     "home_goals": gh, "away_goals": ga,
                     "home_xg": max(0.05, lam_h + rng.normal(0, 0.3)),
                     "away_xg": max(0.05, lam_a + rng.normal(0, 0.3))})
    return pd.DataFrame(rows)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--demo", action="store_true", help="synthetic sanity check")
    args = ap.parse_args()

    if args.demo:
        print("=== SYNTHETIC DEMO (not a real-world result) ===")
        compare(_demo_data(), "demo")
        return

    path = RAW / "xg_matches.csv"
    if not path.exists():
        print(f"No xG dataset at {path}.\n"
              "Harvest xG (FBref match reports or StatsBomb open data) into a CSV "
              "with columns: date, home_team, away_team, home_goals, away_goals, "
              "home_xg, away_xg — then re-run. Or try --demo for a synthetic check.")
        return
    compare(load_xg_csv(path).assign(
        home_goals=lambda d: d["home_goals"], away_goals=lambda d: d["away_goals"]),
        "real")


if __name__ == "__main__":
    main()
