"""Stage 25: spatial team-style profiles from StatsBomb x,y data (the spice).

Builds per-team spatial signals — where they shoot from, how high they play,
how aggressively they press — from event locations. Save to
data/processed/spatial_profiles_<year>.csv and print the standouts.

    python scripts/25_spatial.py --year 2022

These are exploratory STYLE features: feed them as covariates and keep only what
lowers RPS on the EVALUATION scoreboard.
"""

import argparse

from wc2026.config import PROCESSED, ensure_dirs
from wc2026.data.statsbomb import team_spatial_profiles


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--year", type=int, default=2022, choices=[2018, 2022])
    args = ap.parse_args()

    ensure_dirs()
    print(f"Building spatial profiles from StatsBomb {args.year} event locations...")
    df = team_spatial_profiles(args.year)
    out = PROCESSED / f"spatial_profiles_{args.year}.csv"
    df.to_csv(out, index=False)

    print(f"\nMost territorial (play highest up the pitch):")
    print(df.head(6)[["team", "territory", "box_share", "shot_dist",
                      "press_height"]].to_string(index=False))
    print("\nHighest press (defensive actions in attacking half):")
    print(df.nlargest(6, "press_height")[["team", "press_height", "territory"]]
          .to_string(index=False))
    print("\nBest shot locations (closest avg shot to goal):")
    print(df.nsmallest(6, "shot_dist")[["team", "shot_dist", "box_share"]]
          .to_string(index=False))
    print(f"\nsaved -> {out}")


if __name__ == "__main__":
    main()
