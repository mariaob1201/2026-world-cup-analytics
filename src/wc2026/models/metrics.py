"""Scoring rules for evaluating 1X2 (win/draw/loss) + goals forecasts.

You can't improve what you can't benchmark. These are the proper scoring rules
for football outcome forecasts:

* **RPS** (Ranked Probability Score) — the football standard. Unlike Brier it is
  *ordinal-aware*: predicting a win when it was a draw is penalized less than
  predicting a win when it was a loss. Lower is better.
* **log-loss** — penalizes confident wrong calls hardest. Lower is better.
* **Brier** (3-class), **outcome hit-rate**, **goals MAE** — kept for continuity.

Every metric works per-row and aggregates by mean, so models and baselines are
compared on the same matches.
"""

from __future__ import annotations

import numpy as np

ORDER = ("H", "D", "A")          # ordinal result scale (home win → draw → away win)
_ONEHOT = {"H": (1, 0, 0), "D": (0, 1, 0), "A": (0, 0, 1)}


def rps(p_home: float, p_draw: float, p_away: float, result: str) -> float:
    """Ranked Probability Score for one match (0 = perfect, lower better)."""
    p = np.array([p_home, p_draw, p_away], float)
    o = np.array(_ONEHOT[result], float)
    cp, co = np.cumsum(p), np.cumsum(o)
    return float(np.sum((cp[:-1] - co[:-1]) ** 2) / (len(p) - 1))


def log_loss(p_home: float, p_draw: float, p_away: float, result: str) -> float:
    p = {"H": p_home, "D": p_draw, "A": p_away}[result]
    return float(-np.log(max(p, 1e-12)))


def brier(p_home: float, p_draw: float, p_away: float, result: str) -> float:
    p = np.array([p_home, p_draw, p_away], float)
    o = np.array(_ONEHOT[result], float)
    return float(np.sum((p - o) ** 2))


def predicted_result(p_home: float, p_draw: float, p_away: float) -> str:
    return ORDER[int(np.argmax([p_home, p_draw, p_away]))]


def evaluate(rows) -> dict:
    """Aggregate metrics over an iterable of dicts with keys:
    p_H, p_D, p_A, result, and optionally pred_total / actual_total (goals).
    """
    rows = list(rows)
    if not rows:
        return {}
    rps_v = np.mean([rps(r["p_H"], r["p_D"], r["p_A"], r["result"]) for r in rows])
    ll = np.mean([log_loss(r["p_H"], r["p_D"], r["p_A"], r["result"]) for r in rows])
    br = np.mean([brier(r["p_H"], r["p_D"], r["p_A"], r["result"]) for r in rows])
    hit = np.mean([predicted_result(r["p_H"], r["p_D"], r["p_A"]) == r["result"]
                   for r in rows])
    out = {"n": len(rows), "RPS": round(float(rps_v), 4),
           "log_loss": round(float(ll), 4), "Brier": round(float(br), 4),
           "hit_rate": round(float(hit), 3)}
    goals = [r for r in rows if r.get("pred_total") is not None
             and r.get("actual_total") is not None]
    if goals:
        out["goals_MAE"] = round(float(np.mean(
            [abs(r["pred_total"] - r["actual_total"]) for r in goals])), 3)
    return out
