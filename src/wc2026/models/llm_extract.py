"""LLM feature extraction: turn unstructured match/news text into signals.

The "extract features over the games from a live feed" piece. Given a match
report, preview, or news blob, Claude returns STRUCTURED features the model can
use — lineup/formation, injuries & suspensions, and a momentum signal — which
feed the momentum/scouting layers (``models/momentum.py``, ``data/scouting.py``).

Same pattern as the LLM judge: ``claude-opus-4-8`` with structured output and
adaptive thinking, the ``anthropic`` SDK imported lazily, and a no-LLM fallback
so the module loads and tests run offline. Set ANTHROPIC_API_KEY to use it live.
"""

from __future__ import annotations

import os

MODEL = "claude-opus-4-8"

SYSTEM = (
    "You are a football data extractor. From the provided text about a team or "
    "match, extract only what is stated or strongly implied. Do not invent facts. "
    "Return a momentum_signal in [-1, 1]: positive = good form/confidence, "
    "negative = poor form/turmoil, 0 = neutral/unknown."
)


def _schema():
    from pydantic import BaseModel

    class MatchFeatures(BaseModel):
        team: str
        formation: str          # e.g. "4-1-4-1" or "unknown"
        injuries: list[str]
        suspensions: list[str]
        likely_xi_changes: list[str]
        momentum_signal: float  # [-1, 1]
        notes: str

    return MatchFeatures


def extract_features(text: str, team: str = "", client=None, model: str = MODEL):
    """Extract structured features from free text. Falls back to a neutral stub."""
    if client is None:
        if not os.environ.get("ANTHROPIC_API_KEY"):
            return _neutral(team)
        try:
            import anthropic
        except ImportError:
            return _neutral(team)
        client = anthropic.Anthropic()

    MatchFeatures = _schema()
    prompt = (f"Team of interest: {team or 'the team named in the text'}.\n\n"
              f"TEXT:\n{text}\n\nExtract the structured features.")
    resp = client.messages.parse(
        model=model, max_tokens=1500, thinking={"type": "adaptive"},
        system=SYSTEM, messages=[{"role": "user", "content": prompt}],
        output_format=MatchFeatures,
    )
    return resp.parsed_output


def _neutral(team: str):
    """Zero-dependency neutral result (no API/SDK)."""
    stub = {"team": team, "formation": "unknown", "injuries": [], "suspensions": [],
            "likely_xi_changes": [], "momentum_signal": 0.0,
            "notes": "No LLM configured — neutral stub."}
    try:
        return _schema()(**stub)
    except Exception:
        return stub


def momentum_from_features(features) -> float:
    """Map an extracted momentum_signal to the small shift the model expects."""
    sig = getattr(features, "momentum_signal", None)
    if sig is None and isinstance(features, dict):
        sig = features.get("momentum_signal", 0.0)
    return max(-0.10, min(0.10, 0.10 * float(sig or 0.0)))
