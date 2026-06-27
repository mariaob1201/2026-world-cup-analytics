# 🔮 WC 2026 — Winners: next-day picks + champion scorecard

_A simple **Elo** model, conditioned on the **60 matches played so far** and the real 2026 bracket. Updated 2026-06-26._

## Next match day — who wins (Elo goals model)

_Elo gap → two Poisson scoring rates → 1X2 + likely score. Date: **2026-06-27**._

| Fixture | Elo | Pred goals | Likely | P(H/D/A) | **Pick** |
|---|---|---|---|---|---|
| Panama v England | 1350 v 1584 | 1.0-1.9 | 0-1 | 19%/22%/59% | **England** (59%) |
| Algeria v Austria | 1536 v 1553 | 1.3-1.4 | 1-1 | 36%/26%/39% | **Austria** (39%) |
| Jordan v Argentina | 1376 v 1717 | 0.8-2.2 | 0-2 | 13%/19%/69% | **Argentina** (69%) |
| Colombia v Portugal | 1647 v 1704 | 1.2-1.5 | 1-1 | 32%/26%/42% | **Portugal** (42%) |
| Congo DR v Uzbekistan | 1422 v 1415 | 1.4-1.3 | 1-1 | 38%/26%/36% | **Congo DR** (38%) |
| Croatia v Ghana | 1524 v 1409 | 1.6-1.1 | 1-1 | 48%/25%/27% | **Croatia** (48%) |

## Champion scorecard — simulated from today's state

_8,000 Elo tournaments. Played group games are held fixed; the rest of the groups + the knockout bracket are simulated. Teams already out fall to ~0%._

| # | Team | R16 | QF | SF | Final | **Champion** |
|--:|---|---|---|---|---|---|
| 1 | Argentina | 87% | 48% | 26% | 16% | **11%** |
| 2 | Spain | 86% | 48% | 24% | 15% | **10%** |
| 3 | France | 86% | 47% | 24% | 15% | **10%** |
| 4 | Portugal | 84% | 46% | 23% | 13% | **9%** |
| 5 | Brazil | 78% | 46% | 29% | 13% | **8%** |
| 6 | Colombia | 75% | 40% | 23% | 10% | **6%** |
| 7 | Netherlands | 66% | 38% | 22% | 12% | **5%** |
| 8 | Mexico | 70% | 40% | 19% | 8% | **4%** |
| 9 | Morocco | 68% | 37% | 17% | 6% | **4%** |
| 10 | Switzerland | 60% | 32% | 17% | 9% | **4%** |
| 11 | Japan | 62% | 33% | 18% | 10% | **4%** |
| 12 | England | 58% | 32% | 16% | 9% | **3%** |
| 13 | Germany | 57% | 30% | 17% | 9% | **3%** |
| 14 | Ecuador | 57% | 30% | 17% | 8% | **3%** |
| 15 | Ivory Coast | 54% | 28% | 15% | 7% | **3%** |
| 16 | Austria | 46% | 24% | 11% | 6% | **2%** |

## Track record — predicted vs true winners (out-of-sample)

_Each WC match was predicted from Elo as it stood **before** that game (then the rating updated). Running accuracy: **58%** on 60 matches. Full log: `data/processed/winners_track.csv`._

| Date | Fixture | Score | Predicted | Actual | ✓ |
|---|---|---|---|---|:--:|
| 2026-06-24 | Mexico v Czechia | 3-0 | Mexico | **Mexico** | ✅ |
| 2026-06-24 | South Africa v South Korea | 1-0 | South Korea | **South Africa** | — |
| 2026-06-24 | Canada v Switzerland | 1-2 | Canada | **Switzerland** | — |
| 2026-06-24 | Bosnia-Herzegovina v Qatar | 3-1 | Bosnia-Herzegovina | **Bosnia-Herzegovina** | ✅ |
| 2026-06-24 | Scotland v Brazil | 0-3 | Brazil | **Brazil** | ✅ |
| 2026-06-24 | Morocco v Haiti | 4-2 | Morocco | **Morocco** | ✅ |
| 2026-06-25 | United States v Türkiye | 2-3 | United States | **Türkiye** | — |
| 2026-06-25 | Paraguay v Australia | 0-0 | Australia | **Draw** | — |
| 2026-06-25 | Curaçao v Ivory Coast | 0-2 | Ivory Coast | **Ivory Coast** | ✅ |
| 2026-06-25 | Ecuador v Germany | 2-1 | Germany | **Ecuador** | — |
| 2026-06-25 | Japan v Sweden | 1-1 | Japan | **Draw** | — |
| 2026-06-25 | Tunisia v Netherlands | 1-3 | Netherlands | **Netherlands** | ✅ |

_Showing the latest 12 of 60. Elo hit-rate vs a coin-flip baseline is the honest scoreboard for these picks._


## Method (simple by design)

- **Elo** is walked over all real results to today (recency- & WC-weighted K, goal-diff multiplier, host edge) — `models/elo.py`.
- **Goals**: Elo gap → two Poisson rates around a 1.35-goal baseline; the scoreline distribution gives 1X2.
- **Conditioning**: completed group games are fixed, so the scorecard reflects the actual standings — not a fresh re-roll.
- **LLM judge** (`--llm`) is an optional qualitative overlay on the next-day picks; see `models/llm_judge.py`.
- For the fuller Bayesian goals model (squad-skill prior + form + sentiment) see [CHAMPION_TRACKER.md](CHAMPION_TRACKER.md).