"""Social/semantic sentiment features — the 'buzz' spice.

Turn social-media / news text about each team into a sentiment score, then into
a small, capped goal-rate nudge that can condition predictions. Uses the LLM
feature extractor (OpenAI or Claude, provider-agnostic) to read the text; with
no LLM key configured every team scores neutral (0), so it's safe by default.

Honest framing: this is **exploratory**. Sentiment is a weak, noisy signal — keep
its weight small (it is capped here) and only trust it if it lowers RPS on the
EVALUATION scoreboard. You supply the per-team text (X via the budget-capped
collector, news, fan forums); the scoring is automated.
"""

from __future__ import annotations

CAP = 0.12          # max goal-rate nudge from sentiment (small on purpose)
SCALE = 0.10


def social_sentiment(team_texts: dict[str, str]) -> dict[str, float]:
    """team -> social/news text blob  =>  sentiment score in [-1, 1] per team."""
    from ..models.llm_extract import extract_features

    scores = {}
    for team, text in team_texts.items():
        f = extract_features(text, team=team)
        sig = getattr(f, "momentum_signal", None)
        if sig is None and isinstance(f, dict):
            sig = f.get("momentum_signal", 0.0)
        scores[team] = float(sig or 0.0)
    return scores


def sentiment_shifts(scores: dict[str, float]) -> dict[str, float]:
    """Map sentiment scores to small, capped goal-rate nudges for predict_match."""
    return {t: max(-CAP, min(CAP, SCALE * s)) for t, s in scores.items()}
