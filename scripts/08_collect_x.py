"""Collect X (Twitter) fan sentiment — budget-safe.

Examples
--------
    export X_BEARER_TOKEN="AAAA..."
    python scripts/08_collect_x.py --probe                 # ~$0.06 sanity test
    python scripts/08_collect_x.py --query "Mexico World Cup" --max 50 --lang en

Every run prints a cost estimate and refuses to read more than 100 posts.
Results are saved to data/raw/ and summarised with the (swappable) lexicon
sentiment scorer.
"""

import argparse
import json

from wc2026.config import RAW, ensure_dirs
from wc2026.data.x_collector import (
    MAX_RESULTS_CAP,
    estimate_cost,
    probe,
    save,
    search_recent,
    summarize_for_scouting,
)


def main() -> None:
    p = argparse.ArgumentParser(description="Budget-safe X sentiment collector")
    p.add_argument("--probe", action="store_true",
                   help="cheapest end-to-end test (auth + ~10 posts)")
    p.add_argument("--query", default="Mexico World Cup", help="search query")
    p.add_argument("--max", type=int, default=50,
                   help=f"posts to fetch (hard cap {MAX_RESULTS_CAP})")
    p.add_argument("--lang", default=None, help="language filter, e.g. en or es")
    args = p.parse_args()

    ensure_dirs()

    if args.probe:
        result = probe()
        print("\nProbe OK:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    print(f"Planned spend: ~${estimate_cost(min(args.max, MAX_RESULTS_CAP)):.2f}")
    tweets = search_recent(args.query, max_results=args.max, lang=args.lang)

    slug = args.query.lower().replace(" ", "_")[:40]
    save(tweets, RAW / f"x_{slug}.json")

    summary = summarize_for_scouting(tweets)
    print("\n=== Sentiment summary ===")
    print(f"net mood: {summary['net_mood']}  "
          f"(+{summary['pos']} / -{summary['neg']} / ={summary['neutral']} "
          f"of {summary['n']})")
    if summary["positive"]:
        print("\nTop positive:")
        for t in summary["positive"]:
            print(f"  + {t}")
    if summary["negative"]:
        print("\nTop negative:")
        for t in summary["negative"]:
            print(f"  - {t}")
    print(f"\n_{summary.get('caveat', '')}_")


if __name__ == "__main__":
    main()
