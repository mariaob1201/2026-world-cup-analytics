"""Stage 19: evaluation harness — backtest the model across multiple World Cups
against baselines, with proper scoring rules.

For each tournament we fit the Bayesian goals model on the 4 years of results
BEFORE it (no player prior — isolating the match-data model), predict every
match, and score it with RPS / log-loss / Brier / hit-rate / goals-MAE against:
  * **Elo** (recency-weighted ratings → 1X2), and
  * **Naive** (constant home 45% / draw 27% / away 28%).

A model only earns its complexity by beating these. Writes docs/EVALUATION.md.

    python scripts/19_evaluate.py
"""

import numpy as np
import pandas as pd
import pymc as pm

from wc2026.config import ROOT, ensure_dirs
from wc2026.data.sources import download_intl_results
from wc2026.models.bayesian_score import build_model, predict_match, recency_weights
from wc2026.models.elo import BASE_RATING, HFA, _g_multiplier, _k_for, win_probability
from wc2026.models.metrics import evaluate

# Tournament -> (first match date, last date to score). 2026 = group games to date.
WORLD_CUPS = {
    2018: ("2018-06-14", "2018-07-15"),
    2022: ("2022-11-20", "2022-12-18"),
    2026: ("2026-06-11", "2026-06-19"),
}
NAIVE = (0.45, 0.27, 0.28)   # base-rate home/draw/away


def generic_elo(train: pd.DataFrame) -> dict:
    r: dict[str, float] = {}
    for m in train.sort_values("date").itertuples():
        h, a = m.home_team, m.away_team
        adj = 0.0 if bool(getattr(m, "neutral", True)) else HFA
        rh, ra = r.get(h, BASE_RATING), r.get(a, BASE_RATING)
        eh = 1 / (1 + 10 ** (-(rh + adj - ra) / 400))
        gh, ga = int(m.home_score), int(m.away_score)
        w = 1.0 if gh > ga else 0.0 if gh < ga else 0.5
        k = _k_for(m.tournament) * _g_multiplier(gh - ga)
        r[h] = rh + k * (w - eh)
        r[a] = ra - k * (w - eh)
    return r


def elo_1x2(rh: float, ra: float, neutral: bool):
    pa = win_probability(rh, ra, neutral=neutral)
    draw = 0.10 + 0.22 * (1 - abs(pa - 0.5) * 2)
    return pa * (1 - draw), draw, (1 - pa) * (1 - draw)


def run_year(df: pd.DataFrame, year: int, start: str, end: str):
    wc = df[(df.tournament == "FIFA World Cup") & (df.date >= start) & (df.date <= end)]
    wc = wc.dropna(subset=["home_score", "away_score"])
    teams = sorted(set(wc.home_team) | set(wc.away_team))
    cutoff = pd.Timestamp(start)
    train = df[(df.date < cutoff) & (df.date >= cutoff - pd.Timedelta(days=4 * 365))
               & df.home_team.isin(teams) & df.away_team.isin(teams)].dropna(
                   subset=["home_score", "away_score"])
    elo = generic_elo(train)   # uses home_score/away_score — before the rename
    train_model = train.rename(columns={"home_score": "home_goals",
                                        "away_score": "away_goals"})
    zeros = np.zeros(len(teams))

    def _fit(weights):
        with build_model(train_model, teams, prior_strength=zeros, weights=weights):
            return pm.sample(draws=800, tune=800, chains=2, cores=1,
                             target_accept=0.9, progressbar=False, random_seed=7)

    idata = _fit(None)
    # Recency-weighted variant: down-weight stale matches (18-month half-life).
    w = recency_weights(train_model["date"], cutoff, half_life_days=540)
    idata_rec = _fit(w)

    model_rows, rec_rows, elo_rows, naive_rows = [], [], [], []
    for m in wc.itertuples():
        h, a = m.home_team, m.away_team
        neutral = bool(getattr(m, "neutral", True))
        gh, ga = int(m.home_score), int(m.away_score)
        result = "H" if gh > ga else "A" if ga > gh else "D"
        actual_total = gh + ga

        for src, bucket in ((idata, model_rows), (idata_rec, rec_rows)):
            p = predict_match(src, teams, h, a, neutral=neutral)
            bucket.append({"p_H": p["p_home_win"], "p_D": p["p_draw"],
                           "p_A": p["p_away_win"], "result": result,
                           "pred_total": p["exp_goals_home"] + p["exp_goals_away"],
                           "actual_total": actual_total})
        eh, ed, ea = elo_1x2(elo.get(h, BASE_RATING), elo.get(a, BASE_RATING), neutral)
        elo_rows.append({"p_H": eh, "p_D": ed, "p_A": ea, "result": result})
        naive_rows.append({"p_H": NAIVE[0], "p_D": NAIVE[1], "p_A": NAIVE[2],
                           "result": result})

    return {"year": year, "Bayesian": evaluate(model_rows),
            "Bayesian+recency": evaluate(rec_rows),
            "Elo": evaluate(elo_rows), "Naive": evaluate(naive_rows)}


MODELS = ("Bayesian", "Bayesian+recency", "Elo", "Naive")


def main() -> None:
    ensure_dirs()
    df = download_intl_results()
    results = []
    for year, (start, end) in WORLD_CUPS.items():
        print(f"Backtesting {year}...")
        results.append(run_year(df, year, start, end))

    md = _render(results)
    out = ROOT / "docs" / "EVALUATION.md"
    out.write_text(md)
    print("\n" + _console(results))
    print(f"\nsaved -> {out}")


def _console(results) -> str:
    lines = []
    for r in results:
        d = r["Bayesian+recency"]["RPS"] - r["Bayesian"]["RPS"]
        lines.append(f"[{r['year']}] n={r['Bayesian']['n']}  RPS  "
                     f"Bayes {r['Bayesian']['RPS']} | +recency "
                     f"{r['Bayesian+recency']['RPS']} ({d:+.4f}) | "
                     f"Elo {r['Elo']['RPS']} | Naive {r['Naive']['RPS']}")
    return "\n".join(lines)


def _render(results) -> str:
    L = ["# Model Evaluation — Backtest vs Baselines\n",
         "_Bayesian goals model (no player prior) fit on the 4 years before each "
         "tournament, scored on that tournament's matches against Elo and a naive "
         "base-rate baseline. Lower RPS / log-loss / Brier is better. Compiled "
         "2026-06-19._\n"]
    L.append("**Why these metrics:** RPS is the football-standard ordinal score "
             "(a win-vs-draw miss hurts less than win-vs-loss); log-loss punishes "
             "confident errors; the model must beat Elo and naive to justify itself.\n")
    for r in results:
        L.append(f"## {r['year']} World Cup  (n={r['Bayesian']['n']} matches)\n")
        L.append("| Model | RPS ↓ | log-loss ↓ | Brier ↓ | hit-rate ↑ | goals MAE ↓ |")
        L.append("|---|---|---|---|---|---|")
        for name in MODELS:
            m = r[name]
            L.append(f"| {name} | {m['RPS']} | {m['log_loss']} | {m['Brier']} | "
                     f"{m['hit_rate']} | {m.get('goals_MAE', '—')} |")
        L.append("")
    L.append("## How to use this\n")
    L.append("- This is the **scoreboard**: any model change (recency weighting, "
             "Dixon-Coles, strength-of-schedule, current ratings prior) should move "
             "RPS/log-loss down here before it ships.")
    L.append("- 2026 is a small in-progress sample (one matchday); 2018/2022 are "
             "full tournaments and the more reliable signal.")
    L.append("- Baselines: **Elo** (recency ratings) and **Naive** (constant base "
             "rates). Beating Naive is table stakes; beating Elo is the real bar.")
    return "\n".join(L)


if __name__ == "__main__":
    main()
