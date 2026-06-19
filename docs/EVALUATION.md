# Model Evaluation — Backtest vs Baselines

_Bayesian goals model (no player prior) fit on the 4 years before each tournament, scored on that tournament's matches against Elo and a naive base-rate baseline. Lower RPS / log-loss / Brier is better. Compiled 2026-06-19._

**Why these metrics:** RPS is the football-standard ordinal score (a win-vs-draw miss hurts less than win-vs-loss); log-loss punishes confident errors; the model must beat Elo and naive to justify itself.

## 2018 World Cup  (n=64 matches)

| Model | RPS ↓ | log-loss ↓ | Brier ↓ | hit-rate ↑ | goals MAE ↓ |
|---|---|---|---|---|---|
| Bayesian | 0.2132 | 1.0027 | 0.5994 | 0.594 | 1.175 |
| Bayesian+recency | 0.2111 | 0.9993 | 0.5975 | 0.547 | 1.182 |
| Elo | 0.2153 | 1.0027 | 0.5991 | 0.531 | — |
| Naive | 0.2494 | 1.095 | 0.6651 | 0.391 | — |

## 2022 World Cup  (n=64 matches)

| Model | RPS ↓ | log-loss ↓ | Brier ↓ | hit-rate ↑ | goals MAE ↓ |
|---|---|---|---|---|---|
| Bayesian | 0.2161 | 1.0326 | 0.6168 | 0.5 | 1.488 |
| Bayesian+recency | 0.2153 | 1.0329 | 0.615 | 0.516 | 1.505 |
| Elo | 0.2174 | 1.0269 | 0.6154 | 0.438 | — |
| Naive | 0.2345 | 1.0739 | 0.6497 | 0.438 | — |

## 2026 World Cup  (n=28 matches)

| Model | RPS ↓ | log-loss ↓ | Brier ↓ | hit-rate ↑ | goals MAE ↓ |
|---|---|---|---|---|---|
| Bayesian | 0.1795 | 0.9881 | 0.5951 | 0.5 | 1.515 |
| Bayesian+recency | 0.1799 | 0.9906 | 0.598 | 0.464 | 1.532 |
| Elo | 0.2008 | 1.0728 | 0.6507 | 0.464 | — |
| Naive | 0.1908 | 1.0318 | 0.6188 | 0.536 | — |

## How to use this

- This is the **scoreboard**: any model change (recency weighting, Dixon-Coles, strength-of-schedule, current ratings prior) should move RPS/log-loss down here before it ships.
- 2026 is a small in-progress sample (one matchday); 2018/2022 are full tournaments and the more reliable signal.
- Baselines: **Elo** (recency ratings) and **Naive** (constant base rates). Beating Naive is table stakes; beating Elo is the real bar.