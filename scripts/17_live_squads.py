"""Stage 17: fetch the REAL current 2026 squads from Wikipedia.

Fixes the FIFA-vintage roster problem (e.g. retired players). Saves the real
call-ups — name, position, age (seniority), caps (longevity), club — to
data/processed/live_squads.csv.

    python scripts/17_live_squads.py
"""

import pandas as pd

from wc2026.config import PROCESSED, ensure_dirs
from wc2026.data.live_squads import fetch_squads


def main() -> None:
    ensure_dirs()
    print("Fetching real 2026 squads from Wikipedia...")
    df = fetch_squads()
    df.to_csv(PROCESSED / "live_squads.csv", index=False)

    print(f"  {len(df)} players across {df['team'].nunique()} teams "
          f"-> {PROCESSED / 'live_squads.csv'}")
    # Quick seniority/experience snapshot per team (top of the list).
    agg = (df.groupby("team")
           .agg(players=("name", "size"), avg_age=("age", "mean"),
                total_caps=("caps", "sum"))
           .sort_values("total_caps", ascending=False))
    agg["avg_age"] = agg["avg_age"].round(1)
    print("\nMost experienced squads (by total caps):")
    print(agg.head(8).to_string())
    print("\nExample — Mexico (real call-ups, no vintage names):")
    mex = df[df.team == "Mexico"].nlargest(6, "caps")[["name", "position", "age", "caps"]]
    print(mex.to_string(index=False))


if __name__ == "__main__":
    main()
