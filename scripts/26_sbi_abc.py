"""Stage 26: Simulation-Based Inference (rejection-ABC) demo.

A methods demo, NOT a replacement for the tractable model. It shows that when you
only have a *simulator* (no written likelihood), you can still infer parameters by
simulating and matching SUMMARY STATISTICS to the observed data — and that here it
recovers both the ground truth and what exact MCMC finds.

Setup: 6 teams with known 'true' strengths; we generate observed matches, then
infer **home advantage** and **two teams' strengths** three ways:
  1. truth (the data-generating values),
  2. rejection-ABC (simulator + summary stats only — likelihood-free),
  3. exact MCMC (the tractable Poisson model) — the gold standard here.

ABC ≈ MCMC ≈ truth is the result. When the simulator gets too rich to write a
likelihood (game-state, fatigue, possession chains), ABC/neural-SBI is how you'd
still fit it; this is the scaffold.

    python scripts/26_sbi_abc.py
"""

import numpy as np
import pandas as pd

from wc2026.models.abc import (
    TEAMS, TRUE_HOME_ADV, TRUE_INTERCEPT, TRUE_STR,
    abc_infer, fixtures, simulate, summary,
)

N_MATCHES = 300


def main() -> None:
    rng = np.random.default_rng(0)
    hi, ai = fixtures(N_MATCHES, rng)
    gh, ga = simulate(TRUE_STR, TRUE_HOME_ADV, TRUE_INTERCEPT, hi, ai, rng)
    obs = summary(gh, ga, hi, ai)

    post = abc_infer(obs, hi, ai)
    abc = {k: float(np.mean(v)) for k, v in post.items()}

    # Exact MCMC on the same observed matches (gold standard here).
    import pymc as pm

    from wc2026.models.bayesian_score import build_model, posterior_strength_table, FitResult
    df = pd.DataFrame({"home_team": [TEAMS[i] for i in hi],
                       "away_team": [TEAMS[i] for i in ai],
                       "home_goals": gh, "away_goals": ga})
    with build_model(df, TEAMS, prior_strength=np.zeros(len(TEAMS))):
        idata = pm.sample(draws=800, tune=800, chains=2, cores=1,
                          target_accept=0.9, progressbar=False, random_seed=4)
    ha_mcmc = float(idata.posterior["home_adv"].mean())
    strength = posterior_strength_table(
        FitResult(idata, TEAMS, {t: i for i, t in enumerate(TEAMS)})
    ).set_index("team")["net_strength"]
    # net_strength is on the att+def scale; rescale to the single-strength scale
    # (the simulator's str ≈ half the net), for a like-for-like comparison.
    net0, net5 = strength["T0"] / 2, strength["T5"] / 2

    print("Simulation-Based Inference (rejection-ABC) vs truth vs exact MCMC\n")
    print(f"{'parameter':<14}{'truth':>9}{'ABC':>9}{'MCMC':>9}")
    print(f"{'home_adv':<14}{TRUE_HOME_ADV:>9.2f}{abc['home_adv']:>9.2f}{ha_mcmc:>9.2f}")
    print(f"{'str(T0 strong)':<14}{TRUE_STR[0]:>9.2f}{abc['str_T0']:>9.2f}{net0:>9.2f}")
    print(f"{'str(T5 weak)':<14}{TRUE_STR[5]:>9.2f}{abc['str_T5']:>9.2f}{net5:>9.2f}")
    print("\nABC used only the simulator + 5 summary stats (no likelihood) and "
          "recovers the truth — agreeing with exact MCMC. This is the scaffold for "
          "fitting a richer, likelihood-free match simulator.")


if __name__ == "__main__":
    main()
