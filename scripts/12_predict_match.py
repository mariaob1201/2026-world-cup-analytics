"""Stage 12: predict the GOALS for a single fixture (posterior-predictive).

    python scripts/12_predict_match.py --home Mexico --away Senegal --neutral
"""

import argparse

import arviz as az

from wc2026.config import ARTIFACTS
from wc2026.data.teams import TEAMS
from wc2026.models.bayesian_score import predict_match


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--home", default="Mexico")
    ap.add_argument("--away", default="Senegal")
    ap.add_argument("--neutral", action="store_true", default=True)
    ap.add_argument("--home-advantage", dest="neutral", action="store_false")
    args = ap.parse_args()

    idata = az.from_netcdf(ARTIFACTS / "posterior_real.nc")
    teams = [t.name for t in TEAMS]
    p = predict_match(idata, teams, args.home, args.away, neutral=args.neutral)

    print(f"=== {p['home']} vs {p['away']} "
          f"({'neutral' if p['neutral'] else p['home'] + ' home'}) ===\n")
    print(f"Expected goals:  {p['home']} {p['exp_goals_home']} — "
          f"{p['exp_goals_away']} {p['away']}")
    print(f"Most likely score: {p['most_likely_score']}\n")
    print(f"P({p['home']} win): {100*p['p_home_win']:.0f}%   "
          f"P(draw): {100*p['p_draw']:.0f}%   "
          f"P({p['away']} win): {100*p['p_away_win']:.0f}%")
    print(f"P(over 2.5 goals): {100*p['p_over_2_5']:.0f}%   "
          f"P(both teams score): {100*p['p_btts']:.0f}%")


if __name__ == "__main__":
    main()
