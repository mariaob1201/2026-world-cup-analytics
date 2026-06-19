"""Budget-safe X (Twitter) API v2 collector for fan sentiment.

X moved to **pay-per-use** in 2026 (~$0.005 per post read, ~$0.010 per user
read; migrated accounts got a one-time $10 credit). There is no general free
tier, so this module is built to spend as little as possible while you test:

* ``probe()`` confirms your credentials work and reads just a handful of posts
  (default 10) so a test costs cents, not dollars.
* every fetch is HARD-CAPPED (``MAX_RESULTS_CAP``) so a typo can't drain credit.
* ``estimate_cost()`` prints the $ footprint before and after each call.

Auth: set the env var ``X_BEARER_TOKEN`` (App-only Bearer token). tweepy is an
OPTIONAL dependency, imported lazily — the pure helpers below (sentiment, cost,
summary) import and run without tweepy or a network, so they're unit-testable.

    pip install tweepy
    export X_BEARER_TOKEN="AAAA..."
    python scripts/08_collect_x.py --probe              # ~$0.06 test
    python scripts/08_collect_x.py --query "Mexico World Cup" --max 50
"""

from __future__ import annotations

import json
import os
from pathlib import Path

# --- Pricing (approximate, pay-per-use 2026; verify on your dashboard) ------ #
COST_PER_POST_READ = 0.005
COST_PER_USER_READ = 0.010

# Safety: a single run will never request more than this many posts.
MAX_RESULTS_CAP = 100          # also the per-request max for recent search
PER_REQUEST_MIN = 10           # X recent-search minimum

# Tiny, dependency-free sentiment lexicon. Crude on purpose — swap in a real
# model (HF transformers, or the Claude API) via ``score_texts`` for production.
_POS = {"win", "won", "great", "brilliant", "love", "amazing", "proud", "vamos",
        "solid", "hero", "class", "clutch", "deserved", "beautiful", "goat",
        "clean", "euphoric", "celebrate", "magic", "elite"}
_NEG = {"boo", "boos", "awful", "terrible", "worried", "worry", "bad", "lucky",
        "embarrassing", "choke", "overrated", "lacklustre", "lackluster",
        "boring", "disaster", "shambles", "fraud", "nervous", "poor", "ugly"}


def estimate_cost(n_posts: int, n_users: int = 1) -> float:
    """Approximate $ cost of a collection run."""
    return round(n_posts * COST_PER_POST_READ + n_users * COST_PER_USER_READ, 4)


def _word_set(text: str) -> set[str]:
    return {w.strip(".,!?:;\"'#@()").lower() for w in text.split()}


def score_text(text: str) -> int:
    """+1 net-positive, -1 net-negative, 0 neutral (lexicon heuristic)."""
    w = _word_set(text)
    score = len(w & _POS) - len(w & _NEG)
    return (score > 0) - (score < 0)


def summarize_for_scouting(tweets: list[dict]) -> dict:
    """Aggregate fetched tweets into the MEXICO_SOCIAL-style shape."""
    if not tweets:
        return {"net_mood": "no data", "n": 0, "pos": 0, "neg": 0, "neutral": 0,
                "positive": [], "negative": []}
    scored = [(t, score_text(t.get("text", ""))) for t in tweets]
    pos = [t for t, s in scored if s > 0]
    neg = [t for t, s in scored if s < 0]
    neu = [t for t, s in scored if s == 0]

    def top(items):
        # Most-liked examples make the best illustrative quotes.
        return sorted(items, key=lambda t: t.get("like_count", 0), reverse=True)[:3]

    ratio = len(pos) / max(1, len(pos) + len(neg))
    mood = ("strongly positive" if ratio >= 0.7 else
            "leaning positive" if ratio >= 0.55 else
            "mixed" if ratio >= 0.45 else
            "leaning negative" if ratio >= 0.3 else "strongly negative")
    return {
        "net_mood": mood,
        "n": len(tweets), "pos": len(pos), "neg": len(neg), "neutral": len(neu),
        "positive": [t.get("text", "")[:200] for t in top(pos)],
        "negative": [t.get("text", "")[:200] for t in top(neg)],
        "caveat": "Lexicon-based sentiment; swap score_text for a model for accuracy.",
    }


# --- Network layer (needs tweepy + X_BEARER_TOKEN) -------------------------- #
def _client():
    token = os.environ.get("X_BEARER_TOKEN")
    if not token:
        raise RuntimeError("Set X_BEARER_TOKEN (App-only Bearer token) first.")
    import tweepy  # lazy: only needed when actually calling X

    return tweepy.Client(bearer_token=token)


def _flatten(resp) -> list[dict]:
    out = []
    for t in (resp.data or []):
        pm = getattr(t, "public_metrics", {}) or {}
        out.append({
            "id": str(t.id),
            "text": t.text,
            "created_at": str(getattr(t, "created_at", "")),
            "lang": getattr(t, "lang", None),
            "like_count": pm.get("like_count", 0),
            "retweet_count": pm.get("retweet_count", 0),
        })
    return out


def search_recent(query: str, max_results: int = 50, lang: str | None = None) -> list[dict]:
    """Search the last ~7 days. Hard-capped at MAX_RESULTS_CAP posts."""
    n = max(PER_REQUEST_MIN, min(int(max_results), MAX_RESULTS_CAP))
    q = f"{query} -is:retweet" + (f" lang:{lang}" if lang else "")
    print(f"[x] querying {n} posts for {q!r}  (~${estimate_cost(n):.2f})")
    resp = _client().search_recent_tweets(
        query=q, max_results=n,
        tweet_fields=["created_at", "public_metrics", "lang"],
    )
    tweets = _flatten(resp)
    print(f"[x] got {len(tweets)} posts  (actual ~${estimate_cost(len(tweets)):.2f})")
    return tweets


def probe(sample: int = 10) -> dict:
    """Cheapest possible end-to-end test: auth check + a tiny search."""
    print("[x] probe: verifying credentials + minimal read...")
    me = _client().get_me()
    handle = getattr(me.data, "username", "unknown")
    print(f"[x] authenticated as @{handle}")
    tweets = search_recent("Mexico World Cup", max_results=sample)
    return {"authenticated_as": handle,
            "estimated_cost": estimate_cost(len(tweets), n_users=1),
            "sample": tweets[:3]}


def save(tweets: list[dict], path: str | Path) -> None:
    Path(path).write_text(json.dumps(tweets, ensure_ascii=False, indent=2))
    print(f"[x] saved {len(tweets)} posts -> {path}")
