# 🔮 WC 2026 — Winners: next-day picks + champion scorecard

_A simple **Elo** model, conditioned on the **60 matches played so far** and the real 2026 bracket. Updated 2026-06-26._

## Next match day — who wins (Elo goals model)

_Elo gap → two Poisson scoring rates → 1X2 + likely score. Date: **2026-06-26**._

| Fixture | Elo | Pred goals | Likely | P(H/D/A) | **Pick** |
|---|---|---|---|---|---|
| Senegal v Iraq | 1455 v 1346 | 1.6-1.2 | 1-1 | 47%/25%/28% | **Senegal** (47%) |
| Norway v France | 1528 v 1712 | 1.0-1.8 | 1-1 | 22%/23%/54% | **France** (54%) |
| Uruguay v Spain | 1520 v 1706 | 1.0-1.8 | 1-1 | 22%/23%/54% | **Spain** (54%) |
| New Zealand v Belgium | 1342 v 1539 | 1.0-1.8 | 1-1 | 21%/23%/56% | **Belgium** (56%) |
| Egypt v Iran | 1535 v 1452 | 1.5-1.2 | 1-1 | 45%/25%/30% | **Egypt** (45%) |
| Cape Verde v Saudi Arabia | 1461 v 1368 | 1.5-1.2 | 1-1 | 46%/25%/29% | **Cape Verde** (46%) |

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

## Method (simple by design)

- **Elo** is walked over all real results to today (recency- & WC-weighted K, goal-diff multiplier, host edge) — `models/elo.py`.
- **Goals**: Elo gap → two Poisson rates around a 1.35-goal baseline; the scoreline distribution gives 1X2.
- **Conditioning**: completed group games are fixed, so the scorecard reflects the actual standings — not a fresh re-roll.
- **LLM judge** (`--llm`) is an optional qualitative overlay on the next-day picks; see `models/llm_judge.py`.
- For the fuller Bayesian goals model (squad-skill prior + form + sentiment) see [CHAMPION_TRACKER.md](CHAMPION_TRACKER.md).