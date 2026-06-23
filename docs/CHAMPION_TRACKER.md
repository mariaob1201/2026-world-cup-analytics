# 🏆 World Cup 2026 — Champion Tracker

_A living, state-aware forecast. Conditioned on the **44 matches played so far**: completed group games are held fixed; the rest of the tournament is simulated from a Bayesian goals model (squad-skill prior + current form + X/ESPN sentiment). Updated 2026-06-23._

## How to read this

1. **Next games** — predicted goals for the upcoming fixtures.
2. **The trophy** — each team's title probability, given everything that has already happened.

Both come from one model: goals are the primitive; the winner is a simulation over goals. See [METHODOLOGY.md](METHODOLOGY.md).

## Title odds — conditioned on current results

![Title probabilities](../artifacts/champion_tracker.png)

| Team | Quarter | Semi | Final | **Champion** |
|---|---|---|---|---|
| Argentina | 51% | 30% | 19% | **13%** |
| France | 46% | 25% | 15% | **10%** |
| Spain | 42% | 22% | 12% | **7%** |
| Brazil | 45% | 23% | 11% | **7%** |
| Colombia | 42% | 22% | 11% | **6%** |
| Belgium | 39% | 21% | 11% | **6%** |
| Portugal | 37% | 19% | 10% | **6%** |
| Germany | 41% | 22% | 11% | **6%** |
| Japan | 37% | 20% | 10% | **5%** |
| Morocco | 31% | 16% | 8% | **4%** |
| Switzerland | 31% | 16% | 8% | **3%** |
| Austria | 31% | 16% | 7% | **3%** |

_Mexico's Round-of-32 opponent odds (per candidate): [R32_ODDS.md](R32_ODDS.md) — `make r32-odds`._


## Next games — predicted goals

| Date | Fixture | Pred goals (xG) | Likely | P(H/D/A) | Home form |
|---|---|---|---|---|---|
| 2026-06-24 | Morocco v Haiti | 1.8-0.6 | 1-0 | 66%/22%/12% | rising |
| 2026-06-24 | Bosnia-Herzegovina v Qatar | 1.7-1.0 | 1-0 | 53%/24%/23% | dipping |
| 2026-06-24 | Scotland v Brazil | 0.9-2.0 | 0-1 | 16%/21%/63% | steady |
| 2026-06-24 | South Africa v South Korea | 1.0-0.8 | 0-0 | 37%/33%/30% | dipping |
| 2026-06-24 | Mexico v Czechia | 1.8-0.8 | 1-0 | 62%/22%/16% | rising |
| 2026-06-24 | Canada v Switzerland | 1.4-1.3 | 1-1 | 38%/26%/36% | red-hot |

## Current group standings (played)

| Team | P | Pts | GD |
|---|---|---|---|
| Germany | 2 | 6 | +7 |
| United States | 2 | 6 | +5 |
| France | 2 | 6 | +5 |
| Argentina | 2 | 6 | +5 |
| Norway | 2 | 6 | +4 |
| Mexico | 2 | 6 | +3 |
| Canada | 2 | 4 | +6 |
| Netherlands | 2 | 4 | +4 |
| Japan | 2 | 4 | +4 |
| Spain | 2 | 4 | +4 |
| Switzerland | 2 | 4 | +3 |
| Brazil | 2 | 4 | +3 |
| Egypt | 2 | 4 | +2 |
| Morocco | 2 | 4 | +1 |
| Colombia | 1 | 3 | +2 |
| England | 1 | 3 | +2 |
| Ghana | 1 | 3 | +1 |
| South Korea | 2 | 3 | +0 |
| Scotland | 2 | 3 | +0 |
| Australia | 2 | 3 | +0 |
| Ivory Coast | 2 | 3 | +0 |
| Sweden | 2 | 3 | +0 |
| Austria | 2 | 3 | +0 |
| Paraguay | 2 | 3 | -2 |
| Algeria | 2 | 3 | -2 |
| Belgium | 2 | 2 | +0 |
| Iran | 2 | 2 | +0 |
| Cape Verde | 2 | 2 | +0 |
| Uruguay | 2 | 2 | +0 |
| Portugal | 1 | 1 | +0 |
| Congo DR | 1 | 1 | +0 |
| Czechia | 2 | 1 | -1 |
| Ecuador | 2 | 1 | -1 |
| South Africa | 2 | 1 | -2 |
| New Zealand | 2 | 1 | -2 |
| Bosnia-Herzegovina | 2 | 1 | -3 |
| Saudi Arabia | 2 | 1 | -4 |
| Qatar | 2 | 1 | -6 |
| Curaçao | 2 | 1 | -6 |
| Panama | 1 | 0 | -1 |
| Uzbekistan | 1 | 0 | -2 |
| Croatia | 1 | 0 | -2 |
| Türkiye | 2 | 0 | -3 |
| Senegal | 2 | 0 | -3 |
| Jordan | 2 | 0 | -3 |
| Haiti | 2 | 0 | -4 |
| Iraq | 2 | 0 | -6 |
| Tunisia | 2 | 0 | -8 |

## What feeds the prediction

- **Player skillsets** — squad ratings (pace/shooting/passing/…) and seniority form the model's prior, so squad quality shapes goals.
- **Current results** — the posterior is fit on matches through today and the simulation holds played games fixed.
- **Form + X/ESPN sentiment** — folded in as a small, capped goal-rate nudge (see `models/momentum.py`, `data/scouting.py`).
- **Charts:** `artifacts/champion_tracker.png` (title odds), `artifacts/forecast_probs.png`, `artifacts/calibration.png`.