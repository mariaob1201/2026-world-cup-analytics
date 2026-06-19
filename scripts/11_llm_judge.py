"""Stage 11: LLM-as-a-Judge for a specific 2026 knockout fixture.

Defaults to Mexico's projected Round-of-32 tie (vs Senegal at the Estadio
Azteca, per Opta) and fuses Elo + Bayesian strength + scouted form/tactics/
sentiment into a judged forecast.

    python scripts/11_llm_judge.py                 # Mexico vs Senegal (default)
    python scripts/11_llm_judge.py --a Mexico --b Senegal --stage "Round of 32"

Without ANTHROPIC_API_KEY it prints the Elo-only fallback and says so.
"""

import argparse
import os

import pandas as pd

from wc2026.config import PROCESSED
from wc2026.data.scouting import MEXICO, MEXICO_MEDIA
from wc2026.models.llm_judge import Fixture, TeamContext, judge_match


def _ctx(team: str, elo_df, bayes_df, **extra) -> TeamContext:
    e = elo_df[elo_df.team == team]
    ns = None
    if bayes_df is not None and (bayes_df.team == team).any():
        ns = float(bayes_df[bayes_df.team == team]["net_strength"].iloc[0])
    return TeamContext(
        name=team,
        elo=float(e["elo"].iloc[0]) if len(e) else 1500.0,
        elo_rank=int(e["rank"].iloc[0]) if len(e) else 99,
        net_strength=ns, **extra,
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", default="Mexico")
    ap.add_argument("--b", default="Senegal")
    ap.add_argument("--stage", default="Round of 32")
    ap.add_argument("--venue", default="Estadio Azteca, Mexico City (Mexico home, altitude)")
    args = ap.parse_args()

    elo_df = pd.read_csv(PROCESSED / "elo_ratings.csv")
    bp = PROCESSED / "posterior_strength_real.csv"
    bayes_df = pd.read_csv(bp) if bp.exists() else None

    # Mexico gets the rich scouted context; opponent gets ratings + a stub.
    a_extra = {}
    if args.a == "Mexico":
        a_extra = {
            "recent_form": "Unbeaten in 7; 2 WC clean sheets (2-0 RSA, 1-0 KOR); 5-1 Serbia",
            "squad_profile": "Veteran-led, attack-leaning; talisman incl. Jiménez/Giménez",
            "tactics": f"{MEXICO['preferred_formation']} under {MEXICO['coach']}",
            "sentiment": MEXICO_MEDIA["overall_sentiment"],
        }
    fx = Fixture(
        a=_ctx(args.a, elo_df, bayes_df, **a_extra),
        b=_ctx(args.b, elo_df, bayes_df),
        stage=args.stage, venue=args.venue,
        note="Opta projects this as Mexico's most likely R32 matchup." if args.b == "Senegal" else "",
    )

    # The LLM path needs BOTH the key and the SDK installed.
    using_llm = bool(os.environ.get("ANTHROPIC_API_KEY"))
    try:
        import anthropic  # noqa: F401
    except ImportError:
        using_llm = False
    print(f"Judging: {args.a} vs {args.b} ({args.stage})")
    if using_llm:
        print("Mode: Claude LLM judge (claude-opus-4-8)\n")
    else:
        print("Mode: Elo-only fallback — `pip install anthropic` + set "
              "ANTHROPIC_API_KEY for the real judge\n")

    v = judge_match(fx)
    pa = getattr(v, "p_a_win", None) or v["p_a_win"]
    pd_ = getattr(v, "p_draw", None) or v["p_draw"]
    pb = getattr(v, "p_b_win", None) or v["p_b_win"]
    score = getattr(v, "likely_score", None) or v["likely_score"]
    factors = getattr(v, "key_factors", None) or v["key_factors"]
    rationale = getattr(v, "rationale", None) or v["rationale"]

    print(f"{args.a} win: {100*pa:.0f}%   draw: {100*pd_:.0f}%   {args.b} win: {100*pb:.0f}%")
    print(f"Likely score: {score}")
    print("Key factors: " + "; ".join(factors))
    print(f"\nRationale: {rationale}")


if __name__ == "__main__":
    main()
