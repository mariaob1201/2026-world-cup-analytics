"""LLM-as-a-Judge: Claude judges a specific fixture from the full context.

Where the numbers stop, the judge starts. Elo and the Bayesian model give
strength; this layer hands Claude *everything* — both ratings, recent form, the
squad/tactics profile, fan sentiment, venue/host edge — and asks for calibrated
1X2 probabilities, a likely scoreline, and a rationale. It's the natural way to
"respect the structure and current results" qualitatively: the judge reasons
about a concrete matchup the way an analyst would, fusing signals a single
formula can't.

Design
------
* Uses Claude ``claude-opus-4-8`` with adaptive thinking and **structured
  output** (``messages.parse`` + a Pydantic schema) so the result is validated,
  not regex-scraped.
* The ``anthropic`` SDK is imported lazily — the module loads and the
  Elo-only fallback runs without the SDK or an API key, so tests stay offline.
* ``elo_fallback`` gives deterministic 1X2 probabilities from the Elo gap when
  no key is configured, so the pipeline always produces *something*.

Set ``ANTHROPIC_API_KEY`` to use the real judge:  pip install anthropic
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field

MODEL = "claude-opus-4-8"


@dataclass
class TeamContext:
    name: str
    elo: float
    elo_rank: int
    net_strength: float | None = None   # Bayesian posterior net strength
    recent_form: str = ""
    squad_profile: str = ""
    tactics: str = ""
    sentiment: str = ""


@dataclass
class Fixture:
    a: TeamContext
    b: TeamContext
    stage: str = "Round of 32"
    venue: str = "neutral"               # or e.g. "Estadio Azteca (a's home)"
    note: str = ""


# Pydantic schema is defined lazily so pydantic isn't a hard import for the
# fallback path / tests. anthropic depends on pydantic, so it's present whenever
# the real judge is used.
def _verdict_model():
    from pydantic import BaseModel

    class Verdict(BaseModel):
        p_a_win: float
        p_draw: float
        p_b_win: float
        likely_score: str
        key_factors: list[str]
        rationale: str
        confidence: str  # "low" | "medium" | "high"

    return Verdict


def build_prompt(fx: Fixture) -> str:
    def block(t: TeamContext) -> str:
        ns = f"{t.net_strength:+.2f}" if t.net_strength is not None else "n/a"
        return (f"{t.name}\n"
                f"  - Elo {t.elo:.0f} (rank {t.elo_rank}/48), Bayesian net strength {ns}\n"
                f"  - Recent form: {t.recent_form or 'n/a'}\n"
                f"  - Squad/profile: {t.squad_profile or 'n/a'}\n"
                f"  - Tactics: {t.tactics or 'n/a'}\n"
                f"  - Sentiment: {t.sentiment or 'n/a'}")

    return (
        f"Judge this {fx.stage} fixture and return calibrated win/draw/win "
        f"probabilities (they must sum to ~1), a likely scoreline, the key "
        f"factors, and a short rationale.\n\n"
        f"Venue: {fx.venue}\n{fx.note}\n\n"
        f"TEAM A — {block(fx.a)}\n\nTEAM B — {block(fx.b)}\n\n"
        f"Weigh current form and the venue, not just raw ratings. Be honest "
        f"about uncertainty in a one-off knockout match."
    )


SYSTEM = (
    "You are a rigorous football analyst. You fuse quantitative ratings (Elo, "
    "Bayesian strength) with qualitative scouting (form, tactics, sentiment, "
    "venue) into calibrated, well-reasoned match forecasts. You avoid "
    "overconfidence in single knockout games and you explain your reasoning."
)


def judge_match(fx: Fixture, client=None, model: str = MODEL):
    """Call Claude to judge the fixture; returns a validated Verdict object.

    Falls back to Elo if the SDK/key is unavailable. Pass ``client`` to inject a
    pre-built Anthropic client (e.g. in tests).
    """
    if client is None:
        if not os.environ.get("ANTHROPIC_API_KEY"):
            return _as_verdict(elo_fallback(fx))
        try:
            import anthropic
        except ImportError:
            return _as_verdict(elo_fallback(fx))
        client = anthropic.Anthropic()

    Verdict = _verdict_model()
    response = client.messages.parse(
        model=model,
        max_tokens=2000,
        thinking={"type": "adaptive"},
        system=SYSTEM,
        messages=[{"role": "user", "content": build_prompt(fx)}],
        output_format=Verdict,
    )
    return _normalize(response.parsed_output)


def elo_fallback(fx: Fixture) -> dict:
    """Deterministic 1X2 from the Elo gap — used with no API key (and in tests)."""
    from .elo import win_probability

    neutral = "neutral" in fx.venue.lower()
    p_a_raw = win_probability(fx.a.elo, fx.b.elo, neutral=neutral)
    # Draw likelihood peaks for evenly-matched sides.
    draw = 0.10 + 0.22 * (1 - abs(p_a_raw - 0.5) * 2)
    p_a = p_a_raw * (1 - draw)
    p_b = (1 - p_a_raw) * (1 - draw)
    fav = fx.a if p_a >= p_b else fx.b
    return {
        "p_a_win": round(p_a, 3), "p_draw": round(draw, 3), "p_b_win": round(p_b, 3),
        "likely_score": "1-0" if abs(p_a - p_b) > 0.15 else "1-1",
        "key_factors": [f"Elo gap {fx.a.elo - fx.b.elo:+.0f}",
                        f"{'neutral venue' if neutral else 'venue edge'}"],
        "rationale": (f"Elo-only baseline (no LLM judge configured): {fav.name} "
                      f"favoured on rating."),
        "confidence": "low",
    }


def _normalize(v):
    """Renormalize probabilities to sum to 1 (the model may be slightly off)."""
    total = max(1e-9, v.p_a_win + v.p_draw + v.p_b_win)
    v.p_a_win, v.p_draw, v.p_b_win = (v.p_a_win / total, v.p_draw / total,
                                      v.p_b_win / total)
    return v


def _as_verdict(d: dict):
    """Wrap the fallback dict in the Verdict model when pydantic is available,
    else return the dict (keeps zero-dependency test paths working)."""
    try:
        return _normalize(_verdict_model()(**d))
    except Exception:
        return d
