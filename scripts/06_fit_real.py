"""Stage 06: fit the Bayesian model on REAL international results + REAL player
priors, then save the posterior and a real-data strength table + chart.

Run stage 05 first (it builds team_features_real.csv from the player dataset).
"""

import arviz as az
import pandas as pd

from wc2026.config import ARTIFACTS, PROCESSED, ensure_dirs
from wc2026.data.sources import build_real_matches
from wc2026.data.teams import TEAMS
from wc2026.models.bayesian_score import fit, posterior_strength_table
from wc2026.viz.plots import plot_strength


def main() -> None:
    ensure_dirs()
    matches = build_real_matches(start="2022-01-01", end="2026-06-19")
    print(f"Real international matches (2022-01-01 .. 2026-06-19, our 48 teams): "
          f"{len(matches)}")

    # Prefer the live-roster prior (real 2026 call-ups) when it's been built.
    live_path = PROCESSED / "team_features_live.csv"
    prior_path = live_path if live_path.exists() else PROCESSED / "team_features_real.csv"
    print(f"Prior source: {prior_path.name}")
    team_feat = pd.read_csv(prior_path)
    teams = [t.name for t in TEAMS]
    prior = (team_feat.set_index("team")["prior_strength"]
             .reindex(teams).fillna(0.0).to_numpy())

    print("Sampling posterior on real data (NUTS)...")
    result = fit(matches, teams, prior_strength=prior, draws=1000, tune=1000, chains=4)
    result.idata.to_netcdf(ARTIFACTS / "posterior_real.nc")

    summary = az.summary(result.idata,
                         var_names=["intercept", "home_adv", "beta_prior",
                                    "sigma_att", "sigma_def"])
    print("\nKey-parameter summary (real data):")
    print(summary.to_string())
    print(f"max R-hat: {summary['r_hat'].max():.3f}")

    strength = posterior_strength_table(result)
    strength["rank"] = range(1, len(strength) + 1)
    strength.to_csv(PROCESSED / "posterior_strength_real.csv", index=False)
    plot_strength(strength, ARTIFACTS / "team_strength_real.png")

    print("\nTop 12 by posterior net strength (real data):")
    print(strength.head(12).to_string(index=False))
    mex = strength[strength["team"] == "Mexico"]
    print(f"\nMexico: rank {int(mex['rank'].iloc[0])}/48, "
          f"attack {mex['attack'].iloc[0]:.2f}, defence {mex['defence'].iloc[0]:.2f}")
    print(f"\nsaved -> {PROCESSED / 'posterior_strength_real.csv'}, "
          f"{ARTIFACTS / 'team_strength_real.png'}")


if __name__ == "__main__":
    main()
