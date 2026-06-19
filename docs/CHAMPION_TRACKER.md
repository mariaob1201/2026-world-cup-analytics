# 🏆 World Cup 2026 — Champion Tracker

_A living, state-aware forecast. Conditioned on the **28 matches played so far**: completed group games are held fixed; the rest of the tournament is simulated from a Bayesian goals model (squad-skill prior + current form + X/ESPN sentiment). Updated 2026-06-19._

## How to read this

1. **Next games** — predicted goals for the upcoming fixtures.
2. **The trophy** — each team's title probability, given everything that has already happened.

Both come from one model: goals are the primitive; the winner is a simulation over goals. See [METHODOLOGY.md](METHODOLOGY.md).

## Title odds — conditioned on current results

![Title probabilities](../artifacts/champion_tracker.png)

| Team | Quarter | Semi | Final | **Champion** |
|---|---|---|---|---|
| Argentina | 50% | 29% | 18% | **12%** |
| Belgium | 45% | 24% | 13% | **9%** |
| France | 45% | 23% | 12% | **8%** |
| Colombia | 41% | 22% | 12% | **7%** |
| Portugal | 38% | 20% | 11% | **6%** |
| Germany | 40% | 21% | 11% | **6%** |
| Brazil | 39% | 20% | 10% | **6%** |
| Austria | 37% | 18% | 10% | **5%** |
| Spain | 33% | 18% | 9% | **4%** |
| Switzerland | 31% | 17% | 9% | **4%** |
| Ivory Coast | 31% | 16% | 8% | **4%** |
| England | 29% | 15% | 7% | **3%** |

## Next games — predicted goals

| Date | Fixture | Pred goals (xG) | Likely | P(H/D/A) | Home form |
|---|---|---|---|---|---|
| 2026-06-20 | Netherlands v Sweden | 2.2-1.5 | 2-1 | 53%/20%/27% | steady |
| 2026-06-20 | Tunisia v Japan | 0.6-1.4 | 0-1 | 16%/28%/56% | cold |
| 2026-06-20 | Germany v Ivory Coast | 1.6-1.4 | 1-1 | 44%/24%/33% | red-hot |
| 2026-06-20 | Ecuador v Curaçao | 2.1-0.5 | 1-0 | 73%/18%/8% | steady |
| 2026-06-21 | Belgium v Iran | 2.2-0.7 | 2-0 | 72%/18%/11% | red-hot |
| 2026-06-21 | New Zealand v Egypt | 0.6-1.4 | 0-1 | 18%/28%/54% | cold |
| 2026-06-21 | Spain v Saudi Arabia | 1.6-0.5 | 1-0 | 65%/24%/11% | steady |
| 2026-06-21 | Uruguay v Cape Verde | 1.0-0.8 | 0-0 | 40%/33%/27% | steady |
| 2026-06-22 | France v Iraq | 2.3-0.4 | 2-0 | 79%/16%/6% | rising |
| 2026-06-22 | Norway v Senegal | 1.5-1.2 | 1-1 | 45%/25%/30% | rising |
| 2026-06-22 | Argentina v Austria | 1.7-1.1 | 1-1 | 50%/24%/26% | red-hot |
| 2026-06-22 | Jordan v Algeria | 0.7-1.8 | 0-1 | 14%/23%/63% | dipping |
| 2026-06-23 | Portugal v Uzbekistan | 1.8-0.5 | 1-0 | 68%/22%/10% | rising |
| 2026-06-23 | Colombia v Congo DR | 1.6-0.8 | 1-0 | 57%/25%/18% | rising |
| 2026-06-23 | England v Ghana | 1.9-0.7 | 1-0 | 66%/21%/13% | rising |
| 2026-06-23 | Panama v Croatia | 0.8-1.6 | 0-1 | 19%/25%/56% | dipping |
| 2026-06-24 | Morocco v Haiti | 1.8-0.7 | 1-0 | 62%/23%/15% | rising |
| 2026-06-24 | Bosnia-Herzegovina v Qatar | 1.7-1.1 | 1-0 | 52%/24%/24% | dipping |
| 2026-06-24 | Scotland v Brazil | 1.0-2.0 | 0-1 | 19%/22%/59% | rising |
| 2026-06-24 | South Africa v South Korea | 0.9-0.8 | 0-0 | 37%/33%/30% | dipping |
| 2026-06-24 | Mexico v Czechia | 1.9-0.8 | 1-0 | 62%/22%/16% | rising |
| 2026-06-24 | Canada v Switzerland | 1.4-1.3 | 1-1 | 38%/26%/36% | red-hot |

## Current group standings (played)

| Team | P | Pts | GD |
|---|---|---|---|
| Mexico | 2 | 6 | +3 |
| Canada | 2 | 4 | +6 |
| Switzerland | 2 | 4 | +3 |
| Germany | 1 | 3 | +6 |
| Sweden | 1 | 3 | +4 |
| United States | 1 | 3 | +3 |
| Norway | 1 | 3 | +3 |
| Argentina | 1 | 3 | +3 |
| Australia | 1 | 3 | +2 |
| France | 1 | 3 | +2 |
| Austria | 1 | 3 | +2 |
| Colombia | 1 | 3 | +2 |
| England | 1 | 3 | +2 |
| Scotland | 1 | 3 | +1 |
| Ivory Coast | 1 | 3 | +1 |
| Ghana | 1 | 3 | +1 |
| South Korea | 2 | 3 | +0 |
| Brazil | 1 | 1 | +0 |
| Morocco | 1 | 1 | +0 |
| Netherlands | 1 | 1 | +0 |
| Japan | 1 | 1 | +0 |
| Belgium | 1 | 1 | +0 |
| Egypt | 1 | 1 | +0 |
| Iran | 1 | 1 | +0 |
| New Zealand | 1 | 1 | +0 |
| Spain | 1 | 1 | +0 |
| Cape Verde | 1 | 1 | +0 |
| Saudi Arabia | 1 | 1 | +0 |
| Uruguay | 1 | 1 | +0 |
| Portugal | 1 | 1 | +0 |
| Congo DR | 1 | 1 | +0 |
| Czechia | 2 | 1 | -1 |
| South Africa | 2 | 1 | -2 |
| Bosnia-Herzegovina | 2 | 1 | -3 |
| Qatar | 2 | 1 | -6 |
| Haiti | 1 | 0 | -1 |
| Ecuador | 1 | 0 | -1 |
| Panama | 1 | 0 | -1 |
| Türkiye | 1 | 0 | -2 |
| Senegal | 1 | 0 | -2 |
| Jordan | 1 | 0 | -2 |
| Uzbekistan | 1 | 0 | -2 |
| Croatia | 1 | 0 | -2 |
| Paraguay | 1 | 0 | -3 |
| Iraq | 1 | 0 | -3 |
| Algeria | 1 | 0 | -3 |
| Tunisia | 1 | 0 | -4 |
| Curaçao | 1 | 0 | -6 |

## What feeds the prediction

- **Player skillsets** — squad ratings (pace/shooting/passing/…) and seniority form the model's prior, so squad quality shapes goals.
- **Current results** — the posterior is fit on matches through today and the simulation holds played games fixed.
- **Form + X/ESPN sentiment** — folded in as a small, capped goal-rate nudge (see `models/momentum.py`, `data/scouting.py`).
- **Charts:** `artifacts/champion_tracker.png` (title odds), `artifacts/forecast_probs.png`, `artifacts/calibration.png`.