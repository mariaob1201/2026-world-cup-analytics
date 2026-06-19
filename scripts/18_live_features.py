"""Stage 18: build the model prior from the REAL current squads.

Joins the live Wikipedia roster (real names, positions, age, caps) to skill
ratings and rolls up to a per-team `prior_strength`. Writes
data/processed/team_features_live.csv, which stage 06 prefers over the
FIFA-roster prior when present — so the Bayesian model's prior reflects the
actual 2026 call-ups (the C. Vela fix, all the way through).

    python scripts/17_live_squads.py    # first, to fetch the roster
    python scripts/18_live_features.py
"""

import pandas as pd

from wc2026.config import PROCESSED, RAW, ensure_dirs
from wc2026.data.live_squads import fetch_squads, live_team_features
from wc2026.data.sources import download_fifa


def main() -> None:
    ensure_dirs()
    live_path = PROCESSED / "live_squads.csv"
    live = pd.read_csv(live_path) if live_path.exists() else fetch_squads()
    fifa = download_fifa()

    tf = live_team_features(live, fifa)
    tf.to_csv(PROCESSED / "team_features_live.csv", index=False)

    print(f"Built live-roster prior for {len(tf)} teams "
          f"-> {PROCESSED / 'team_features_live.csv'}")
    print("\nTop 10 by prior_strength (REAL squads + real caps):")
    print(tf.head(10).to_string(index=False))

    # Show the difference the real roster makes vs the FIFA-roster prior.
    old_path = PROCESSED / "team_features_real.csv"
    if old_path.exists():
        old = pd.read_csv(old_path)[["team", "prior_strength"]].rename(
            columns={"prior_strength": "prior_fifa"})
        cmp = tf.merge(old, on="team")
        cmp["delta"] = (cmp["prior_strength"] - cmp["prior_fifa"]).round(3)
        cmp = cmp.reindex(cmp["delta"].abs().sort_values(ascending=False).index)
        print("\nBiggest prior shifts (real roster vs FIFA roster):")
        print(cmp.head(8)[["team", "prior_fifa", "prior_strength", "delta"]]
              .to_string(index=False))


if __name__ == "__main__":
    main()
