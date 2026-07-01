# 🔮 WC 2026 — Winners: next-day picks + champion scorecard

_A simple **Elo** model, conditioned on the **79 matches played so far** and the real 2026 bracket. Updated 2026-07-01._

## Next match day — who wins (Elo goals model)

_Elo gap → two Poisson scoring rates → 1X2 + likely score. Date: **2026-07-02**._

| Fixture | Elo | Pred goals | Likely | P(H/D/A) | **Pick** |
|---|---|---|---|---|---|
| Spain v Austria | 1721 v 1551 | 1.7-1.1 | 1-1 | 53%/24%/23% | **Spain** (53%) |
| Portugal v Croatia | 1699 v 1545 | 1.7-1.1 | 1-1 | 52%/24%/24% | **Portugal** (52%) |
| Switzerland v Algeria | 1585 v 1537 | 1.4-1.3 | 1-1 | 41%/26%/33% | **Switzerland** (41%) |

## Champion scorecard — simulated from today's state

_8,000 Elo tournaments. Played group games are held fixed; the rest of the groups + the knockout bracket are simulated. Teams already out fall to ~0%._

| # | Team | R16 | QF | SF | Final | **Champion** |
|--:|---|---|---|---|---|---|
| 1 | France | 90% | 51% | 30% | 20% | **14%** |
| 2 | Spain | 87% | 51% | 25% | 16% | **11%** |
| 3 | Argentina | 87% | 45% | 24% | 15% | **10%** |
| 4 | Brazil | 80% | 49% | 31% | 14% | **10%** |
| 5 | Portugal | 81% | 42% | 20% | 11% | **8%** |
| 6 | Mexico | 74% | 37% | 21% | 9% | **6%** |
| 7 | Colombia | 71% | 44% | 22% | 9% | **6%** |
| 8 | Netherlands | 66% | 36% | 21% | 13% | **6%** |
| 9 | England | 64% | 35% | 20% | 11% | **4%** |
| 10 | Switzerland | 59% | 32% | 17% | 9% | **3%** |
| 11 | Morocco | 66% | 33% | 15% | 5% | **3%** |
| 12 | Germany | 57% | 29% | 14% | 7% | **3%** |
| 13 | Belgium | 55% | 30% | 16% | 8% | **2%** |
| 14 | Japan | 54% | 27% | 15% | 7% | **2%** |
| 15 | Austria | 52% | 27% | 13% | 6% | **2%** |
| 16 | Ecuador | 50% | 25% | 12% | 6% | **2%** |

## Track record — predicted vs true winners (out-of-sample)

_Each WC match was predicted from Elo as it stood **before** that game (then the rating updated). Running accuracy: **58%** on 79 matches. Full log: `data/processed/winners_track.csv`._

| Date | Fixture | Score | Predicted | Actual | ✓ |
|---|---|---|---|---|:--:|
| 2026-06-27 | Algeria v Austria | 3-3 | Austria | **Draw** | — |
| 2026-06-27 | Jordan v Argentina | 1-3 | Argentina | **Argentina** | ✅ |
| 2026-06-27 | Panama v England | 0-2 | England | **England** | ✅ |
| 2026-06-27 | Croatia v Ghana | 2-1 | Croatia | **Croatia** | ✅ |
| 2026-06-27 | Congo DR v Uzbekistan | 3-1 | Congo DR | **Congo DR** | ✅ |
| 2026-06-28 | South Africa v Canada | 0-1 | South Africa | **Canada** | — |
| 2026-06-29 | Brazil v Japan | 2-1 | Brazil | **Brazil** | ✅ |
| 2026-06-29 | Germany v Paraguay | 1-1 | Germany | **Draw** | — |
| 2026-06-29 | Netherlands v Morocco | 1-1 | Morocco | **Draw** | — |
| 2026-06-30 | Ivory Coast v Norway | 1-2 | Ivory Coast | **Norway** | — |
| 2026-06-30 | France v Sweden | 3-0 | France | **France** | ✅ |
| 2026-06-30 | Mexico v Ecuador | 2-0 | Mexico | **Mexico** | ✅ |

_Showing the latest 12 of 79. Elo hit-rate vs a coin-flip baseline is the honest scoreboard for these picks._


## Method (simple by design)

- **Elo** is walked over all real results to today (recency- & WC-weighted K, goal-diff multiplier, host edge) — `models/elo.py`.
- **Goals**: Elo gap → two Poisson rates around a 1.35-goal baseline; the scoreline distribution gives 1X2.
- **Conditioning**: completed group games are fixed, so the scorecard reflects the actual standings — not a fresh re-roll.
- **LLM judge** (`--llm`) is an optional qualitative overlay on the next-day picks; see `models/llm_judge.py`.
- For the fuller Bayesian goals model (squad-skill prior + form + sentiment) see [CHAMPION_TRACKER.md](CHAMPION_TRACKER.md).