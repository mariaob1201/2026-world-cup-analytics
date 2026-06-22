# WC 2026 — Match Predictions vs Reality, and Forecasts

_Model trained on pre-tournament data only (results to 2026-06-10 + FIFA squad prior). Backtest compares those out-of-sample forecasts to the actual scorelines; forecasts cover the next slate. Compiled 2026-06-22._

## Accuracy so far (out-of-sample)

- **Matches scored:** 40
- **Outcome hit-rate:** 60% (predicted W/D/L matched actual)
- **Mean probability on the actual outcome:** 0.43 · **Brier score:** 0.566 (lower is better)
- **Total-goals mean abs error:** 1.55 goals/match

> Read these as a small-sample sanity check (one matchday), not a verdict. Blowouts like Germany 7-1 and Canada 6-0 inflate the goals error — the model is calibrated to typical scorelines, not outliers.

## Backtest — prediction vs actual (played)

| Date | Fixture | Pred xG | Likely | P(H/D/A) | Actual | ✓ |
|---|---|---|---|---|---|:--:|
| 2026-06-11 | Mexico v South Africa | 1.6-0.8 | 1-0 | 54%/25%/20% | **2-0** | ✅ |
| 2026-06-11 | South Korea v Czechia | 1.3-1.5 | 1-1 | 34%/25%/41% | **2-1** | — |
| 2026-06-12 | Canada v Bosnia-Herzegovina | 1.8-0.9 | 1-0 | 57%/23%/19% | **1-1** | — |
| 2026-06-12 | United States v Paraguay | 1.3-1.1 | 1-1 | 41%/28%/31% | **4-1** | ✅ |
| 2026-06-13 | Qatar v Switzerland | 1.0-2.3 | 1-2 | 16%/19%/65% | **1-1** | — |
| 2026-06-13 | Brazil v Morocco | 1.5-1.0 | 1-1 | 47%/26%/27% | **1-1** | — |
| 2026-06-13 | Haiti v Scotland | 0.7-1.6 | 0-1 | 16%/25%/59% | **0-1** | ✅ |
| 2026-06-13 | Australia v Türkiye | 1.3-1.1 | 1-1 | 40%/28%/32% | **2-0** | ✅ |
| 2026-06-14 | Sweden v Tunisia | 1.1-1.2 | 1-1 | 34%/28%/38% | **5-1** | — |
| 2026-06-14 | Netherlands v Japan | 1.2-1.2 | 1-1 | 38%/28%/35% | **2-2** | — |
| 2026-06-14 | Germany v Curaçao | 3.6-0.8 | 3-0 | 84%/10%/6% | **7-1** | ✅ |
| 2026-06-14 | Ivory Coast v Ecuador | 0.7-0.8 | 0-0 | 28%/38%/34% | **1-0** | — |
| 2026-06-15 | Belgium v Egypt | 1.8-0.8 | 1-0 | 60%/23%/17% | **1-1** | — |
| 2026-06-15 | Iran v New Zealand | 1.1-0.8 | 1-0 | 42%/31%/27% | **2-2** | — |
| 2026-06-15 | Spain v Cape Verde | 2.0-0.6 | 1-0 | 68%/20%/11% | **0-0** | — |
| 2026-06-15 | Saudi Arabia v Uruguay | 0.5-1.2 | 0-1 | 16%/30%/53% | **1-1** | — |
| 2026-06-16 | Austria v Jordan | 2.0-0.6 | 1-0 | 70%/20%/10% | **3-1** | ✅ |
| 2026-06-16 | Argentina v Algeria | 1.6-0.9 | 1-0 | 54%/25%/21% | **3-0** | ✅ |
| 2026-06-16 | France v Senegal | 1.6-0.8 | 1-0 | 58%/24%/18% | **3-1** | ✅ |
| 2026-06-16 | Iraq v Norway | 0.9-1.3 | 0-1 | 25%/28%/47% | **1-4** | ✅ |
| 2026-06-17 | Portugal v Congo DR | 1.8-0.6 | 1-0 | 64%/23%/13% | **1-1** | — |
| 2026-06-17 | Uzbekistan v Colombia | 0.5-1.6 | 0-1 | 12%/25%/63% | **1-3** | ✅ |
| 2026-06-17 | England v Croatia | 1.2-1.1 | 1-1 | 36%/28%/36% | **4-2** | ✅ |
| 2026-06-17 | Ghana v Panama | 1.3-1.0 | 1-0 | 44%/28%/28% | **1-0** | ✅ |
| 2026-06-18 | Czechia v South Africa | 1.2-1.0 | 1-0 | 42%/29%/29% | **1-1** | — |
| 2026-06-18 | Mexico v South Korea | 1.9-1.1 | 1-1 | 54%/23%/24% | **1-0** | ✅ |
| 2026-06-18 | Switzerland v Bosnia-Herzegovina | 2.1-1.0 | 1-0 | 61%/21%/18% | **4-1** | ✅ |
| 2026-06-18 | Canada v Qatar | 2.0-0.9 | 1-0 | 62%/21%/17% | **6-0** | ✅ |
| 2026-06-19 | Türkiye v Paraguay | 1.0-1.2 | 1-1 | 31%/28%/40% | **0-1** | ✅ |
| 2026-06-19 | Scotland v Morocco | 0.9-1.3 | 0-1 | 27%/28%/46% | **0-1** | ✅ |
| 2026-06-19 | Brazil v Haiti | 2.5-0.5 | 2-0 | 79%/14%/6% | **3-0** | ✅ |
| 2026-06-19 | United States v Australia | 1.3-1.1 | 1-1 | 42%/27%/30% | **2-0** | ✅ |
| 2026-06-20 | Netherlands v Sweden | 2.0-1.2 | 1-1 | 55%/22%/23% | **5-1** | ✅ |
| 2026-06-20 | Tunisia v Japan | 0.7-1.1 | 0-1 | 25%/32%/43% | **0-4** | ✅ |
| 2026-06-20 | Germany v Ivory Coast | 1.6-1.1 | 1-1 | 47%/25%/28% | **2-1** | ✅ |
| 2026-06-20 | Ecuador v Curaçao | 1.7-0.5 | 1-0 | 68%/23%/10% | **0-0** | — |
| 2026-06-21 | Belgium v Iran | 1.9-0.8 | 1-0 | 62%/22%/16% | **0-0** | — |
| 2026-06-21 | New Zealand v Egypt | 0.8-1.1 | 0-1 | 25%/31%/44% | **1-3** | ✅ |
| 2026-06-21 | Spain v Saudi Arabia | 1.6-0.6 | 1-0 | 59%/26%/15% | **4-0** | ✅ |
| 2026-06-21 | Uruguay v Cape Verde | 1.6-0.5 | 1-0 | 62%/25%/13% | **2-2** | — |

## Forecast — next fixtures (with momentum nudge)

_`Mom` = recency-weighted form (+ scouted sentiment) applied as a small, capped log-rate nudge to each side's goals (home/away)._

| Date | Fixture | Pred xG | Likely | P(H/D/A) | Over 2.5 | Mom H/A |
|---|---|---|---|---|---|---|
| 2026-06-23 | Portugal v Uzbekistan | 1.9-0.4 | 1-0 | 72%/20%/8% | 42% | +0.06/-0.09 |
| 2026-06-23 | Colombia v Congo DR | 1.7-0.7 | 1-0 | 61%/24%/15% | 40% | +0.09/-0.02 |
| 2026-06-23 | England v Ghana | 2.2-0.8 | 2-0 | 70%/18%/12% | 56% | +0.06/-0.11 |
| 2026-06-23 | Panama v Croatia | 0.5-1.6 | 0-1 | 12%/24%/64% | 36% | -0.08/-0.10 |
| 2026-06-24 | Morocco v Haiti | 1.8-0.5 | 1-0 | 68%/22%/10% | 39% | +0.07/-0.03 |
| 2026-06-24 | Bosnia-Herzegovina v Qatar | 1.6-1.3 | 1-1 | 44%/25%/32% | 54% | -0.08/-0.18 |
| 2026-06-24 | Scotland v Brazil | 1.0-2.4 | 1-2 | 16%/18%/66% | 65% | +0.04/+0.14 |
| 2026-06-24 | South Africa v South Korea | 0.9-1.1 | 0-1 | 31%/30%/39% | 33% | -0.07/-0.05 |
| 2026-06-24 | Mexico v Czechia | 1.9-1.2 | 1-1 | 55%/22%/23% | 59% | +0.09/-0.05 |
| 2026-06-24 | Canada v Switzerland | 1.4-1.4 | 1-1 | 38%/25%/38% | 53% | +0.15/+0.12 |

## Squad & player context (forecast teams)

_From real player data: squad rating, average age (seniority), stylistic tilt, and talisman._

| Team | Tier | Squad ovr | Avg age | Style | Talisman |
|---|---|---|---|---|---|
| Portugal | Elite contender | 84.2 | 27.6 | attack-leaning | Cristiano Ronaldo |
| Colombia | Strong side | 79.4 | 29.3 | attack-leaning | J. Cuadrado |
| England | Elite contender | 85.1 | 26.7 | attack-leaning | H. Kane |
| Panama | Developing team | 68.1 | 26.7 | attack-leaning | M. Murillo |
| Morocco | Strong side | 79.2 | 28.8 | well-balanced | A. Hakimi |
| Bosnia-Herzegovina | Developing team | 75.4 | 29.4 | well-balanced | E. Džeko |
| Scotland | Solid outfit | 76.9 | 28.7 | well-balanced | A. Robertson |
| South Africa | Developing team | 70.8 | 28.4 | well-balanced | L. Singh |
| Mexico | Strong side | 79.0 | 30.8 | attack-leaning | C. Vela |
| Canada | Developing team | 73.6 | 27.9 | well-balanced | A. Davies |
| Uzbekistan | Developing team | 68.2 | 27.2 | well-balanced | O. Akhmedov |
| Congo DR | Developing team | 74.2 | 28.1 | attack-leaning | C. Bakambu |
| Ghana | Developing team | 75.8 | 27.0 | well-balanced | T. Partey |
| Croatia | Strong side | 80.6 | 28.2 | attack-leaning | L. Modrić |
| Haiti | Developing team | 64.1 | 25.1 | well-balanced | C. Arcus |
| Qatar | no data | nan | nan | - | - |
| Brazil | Elite contender | 85.4 | 29.9 | well-balanced | Neymar Jr |
| South Korea | Developing team | 74.4 | 28.1 | attack-leaning | H. Son |
| Czechia | Solid outfit | 78.0 | 27.5 | well-balanced | T. Souček |
| Switzerland | Strong side | 79.1 | 27.2 | well-balanced | R. Freuler |

## Notes on method

- **Goals model:** hierarchical Bayesian Poisson — each team's attack/defence fits the data, scorelines are posterior-predictive. See [METHODOLOGY.md](METHODOLOGY.md).
- **Player data** (skillsets, seniority/age, semantic tier) feeds the model's prior and the context table above (FIFA dataset).
- **Public/sentiment sources** (ESPN, SI, social) enrich the Mexico deep-dive ([../data/processed/mexico_assessment.md]) and are wired to extend to other teams via the scouting + X-collector modules.
- **Limitation:** scores are independent Poisson and there is no strength-of-schedule term yet — see METHODOLOGY §10–11.