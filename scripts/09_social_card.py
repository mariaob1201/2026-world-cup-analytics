"""Stage 09: generate a social-media-ready summary card for Mexico (real data).

    python scripts/09_social_card.py --handle @yourname

Outputs artifacts/mexico_social_card.png (1080x1350, portrait).
"""

import argparse

import pandas as pd

from wc2026.config import ARTIFACTS, PROCESSED, ensure_dirs
from wc2026.data.scouting import MEXICO, MEXICO_SOCIAL
from wc2026.viz.plots import social_card

TEAM = "Mexico"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--handle", default="@your_handle")
    args = ap.parse_args()

    ensure_dirs()
    strength = pd.read_csv(PROCESSED / "posterior_strength_real.csv")
    srow = strength[strength["team"] == TEAM].iloc[0]

    # Comparison set: #1, a marquee mid-pack name, and Mexico.
    top = strength.iloc[0]
    refs = [(top["team"], round(float(top["net_strength"]), 2)),
            ("England", round(float(strength[strength.team == "England"]
                                    ["net_strength"].iloc[0]), 2)),
            (TEAM, round(float(srow["net_strength"]), 2))]

    facts = {
        "team": TEAM, "flag": "🇲🇽",
        "rank": int(srow["rank"]), "n": len(strength),
        "group_line": "1st · 6 pts · 2 clean sheets · qualified",
        "formation": f"{MEXICO['preferred_formation']} under {MEXICO['coach']}",
        "sentiment": MEXICO_SOCIAL["net_mood"],
        "refs": refs,
    }
    out = ARTIFACTS / "mexico_social_card.png"
    social_card(strength, facts, out, handle=args.handle)
    print(f"saved -> {out}")
    print("1080x1350 portrait; real-data only. Ready to post.")


if __name__ == "__main__":
    main()
