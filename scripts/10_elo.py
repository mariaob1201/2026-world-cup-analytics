"""Stage 10: Elo ratings over real results, and an Elo-vs-Bayesian comparison.

    python scripts/10_elo.py

Saves data/processed/elo_ratings.csv and prints how the two strength views
agree and disagree (the interesting part).
"""

import pandas as pd

from wc2026.config import PROCESSED, ensure_dirs
from wc2026.data.sources import build_real_matches
from wc2026.models.elo import run_elo


def main() -> None:
    ensure_dirs()
    matches = build_real_matches(start="2022-01-01", end="2026-06-19")
    elo = run_elo(matches)
    elo.to_csv(PROCESSED / "elo_ratings.csv", index=False)

    print(f"Elo over {len(matches)} real internationals (cold-start 1500, "
          f"WC-weighted K).\n")
    print("Top 12 by Elo:")
    print(elo.head(12).to_string(index=False))

    # Compare with the Bayesian net-strength ranking if it exists (stage 06).
    bayes_path = PROCESSED / "posterior_strength_real.csv"
    if bayes_path.exists():
        bayes = pd.read_csv(bayes_path)[["team", "net_strength", "rank"]]
        bayes = bayes.rename(columns={"rank": "bayes_rank"})
        merged = elo.rename(columns={"rank": "elo_rank"}).merge(bayes, on="team")
        merged["rank_gap"] = merged["bayes_rank"] - merged["elo_rank"]
        print("\nBiggest Elo-vs-Bayesian disagreements (|rank gap|):")
        cols = ["team", "elo", "elo_rank", "net_strength", "bayes_rank", "rank_gap"]
        print(merged.reindex(merged["rank_gap"].abs().sort_values(ascending=False).index)
              .head(8)[cols].to_string(index=False))
    print(f"\nsaved -> {PROCESSED / 'elo_ratings.csv'}")


if __name__ == "__main__":
    main()
