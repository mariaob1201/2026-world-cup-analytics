# 🏆 World Cup 2026 — Champion Tracker

_A living, state-aware forecast. Conditioned on the **79 matches played so far**: completed group games are held fixed; the rest of the tournament is simulated from a Bayesian goals model (squad-skill prior + current form + X/ESPN sentiment). Updated 2026-07-01._

## How to read this

1. **Next games** — predicted goals for the upcoming fixtures.
2. **The trophy** — each team's title probability, given everything that has already happened.

Both come from one model: goals are the primitive; the winner is a simulation over goals. See [METHODOLOGY.md](METHODOLOGY.md).

## Title odds — conditioned on current results

![Title probabilities](../artifacts/champion_tracker.png)

| Team | Quarter | Semi | Final | **Champion** |
|---|---|---|---|---|
| France | 48% | 27% | 16% | **12%** |
| Argentina | 48% | 27% | 16% | **11%** |
| Portugal | 47% | 26% | 15% | **11%** |
| Brazil | 44% | 22% | 11% | **7%** |
| Belgium | 44% | 23% | 11% | **7%** |
| Spain | 43% | 23% | 11% | **6%** |
| Colombia | 40% | 21% | 10% | **6%** |
| Germany | 36% | 19% | 9% | **4%** |
| Netherlands | 31% | 17% | 9% | **3%** |
| Japan | 31% | 16% | 8% | **3%** |
| Switzerland | 31% | 16% | 9% | **3%** |
| Morocco | 32% | 17% | 8% | **3%** |

_Mexico's Round-of-32 opponent odds (per candidate): [R32_ODDS.md](R32_ODDS.md) — `make r32-odds`._


## Title odds over time — the movie, not the snapshot

_How each contender's championship probability moved as matches were played. The x-axis is the **cumulative number of matches played across all teams** (the group stage has 72 in total; each team plays 3), not games-per-team and not an abstract t. Built with a fast Elo simulation re-run after every matchday, conditioned only on results known by then — no look-ahead. `make timeline`._

![Title odds timeline](../artifacts/champion_timeline.png)


## Next games — predicted goals

| Date | Fixture | Pred goals (xG) | Likely | P(H/D/A) | Home form |
|---|---|---|---|---|---|
| 2026-07-01 | United States v Bosnia-Herzegovina | 2.3-1.2 | 2-1 | 62%/19%/19% | steady |
| 2026-07-01 | Belgium v Senegal | 2.3-1.2 | 2-1 | 62%/19%/19% | red-hot |
| 2026-07-01 | England v Congo DR | 1.2-0.9 | 1-0 | 44%/29%/27% | rising |
| 2026-07-02 | Spain v Austria | 1.9-1.3 | 1-1 | 51%/22%/27% | rising |
| 2026-07-02 | Portugal v Croatia | 1.7-0.8 | 1-0 | 59%/24%/17% | red-hot |
| 2026-07-02 | Switzerland v Algeria | 1.7-1.3 | 1-1 | 48%/23%/29% | rising |
| 2026-07-03 | Australia v Egypt | 0.9-1.0 | 0-0 | 34%/32%/35% | steady |
| 2026-07-03 | Argentina v Cape Verde | 1.9-0.6 | 1-0 | 67%/21%/12% | red-hot |
| 2026-07-03 | Colombia v Ghana | 2.0-0.5 | 1-0 | 72%/19%/9% | rising |
| 2026-07-04 | Canada v Morocco | 1.0-1.1 | 0-1 | 32%/30%/38% | rising |
| 2026-07-04 | Paraguay v France | 0.7-1.9 | 0-1 | 13%/21%/66% | steady |
| 2026-07-05 | Brazil v Norway | 2.5-1.2 | 2-1 | 65%/18%/17% | red-hot |

## Current group standings (played)

| Team | P | Pts | GD |
|---|---|---|---|
| France | 4 | 12 | +11 |
| Mexico | 4 | 12 | +8 |
| Brazil | 4 | 10 | +7 |
| Argentina | 3 | 9 | +7 |
| Norway | 4 | 9 | +2 |
| Netherlands | 4 | 8 | +6 |
| Morocco | 4 | 8 | +3 |
| Canada | 4 | 7 | +6 |
| Germany | 4 | 7 | +6 |
| Spain | 3 | 7 | +5 |
| Switzerland | 3 | 7 | +4 |
| England | 3 | 7 | +4 |
| Colombia | 3 | 7 | +3 |
| United States | 3 | 6 | +4 |
| Ivory Coast | 4 | 6 | +1 |
| Croatia | 3 | 6 | +0 |
| Portugal | 3 | 5 | +5 |
| Belgium | 3 | 5 | +4 |
| Japan | 4 | 5 | +3 |
| Egypt | 3 | 5 | +2 |
| Paraguay | 4 | 5 | -2 |
| Congo DR | 3 | 4 | +1 |
| Australia | 3 | 4 | +0 |
| Austria | 3 | 4 | +0 |
| Ghana | 3 | 4 | +0 |
| Bosnia-Herzegovina | 3 | 4 | -1 |
| South Africa | 4 | 4 | -2 |
| Ecuador | 4 | 4 | -2 |
| Algeria | 3 | 4 | -2 |
| Sweden | 4 | 4 | -3 |
| Senegal | 3 | 3 | +2 |
| Iran | 3 | 3 | +0 |
| Cape Verde | 3 | 3 | +0 |
| South Korea | 3 | 3 | -1 |
| Türkiye | 3 | 3 | -2 |
| Scotland | 3 | 3 | -3 |
| Uruguay | 3 | 2 | -1 |
| Saudi Arabia | 3 | 2 | -4 |
| Czechia | 3 | 1 | -4 |
| New Zealand | 3 | 1 | -6 |
| Qatar | 3 | 1 | -8 |
| Curaçao | 3 | 1 | -8 |
| Panama | 3 | 0 | -4 |
| Jordan | 3 | 0 | -5 |
| Haiti | 3 | 0 | -6 |
| Uzbekistan | 3 | 0 | -9 |
| Tunisia | 3 | 0 | -10 |
| Iraq | 3 | 0 | -11 |

## What feeds the prediction

- **Player skillsets** — squad ratings (pace/shooting/passing/…) and seniority form the model's prior, so squad quality shapes goals.
- **Current results** — the posterior is fit on matches through today and the simulation holds played games fixed.
- **Form + X/ESPN sentiment** — folded in as a small, capped goal-rate nudge (see `models/momentum.py`, `data/scouting.py`).
- **Charts:** `artifacts/champion_tracker.png` (title odds), `artifacts/forecast_probs.png`, `artifacts/calibration.png`.