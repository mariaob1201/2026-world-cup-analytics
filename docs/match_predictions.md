# WC 2026 — Match Predictions vs Reality, and Forecasts

_Model trained on pre-tournament data only (results to 2026-06-10 + FIFA squad prior). Backtest compares those out-of-sample forecasts to the actual scorelines; forecasts cover the next slate. Compiled 2026-06-19._

## Accuracy so far (out-of-sample)

- **Matches scored:** 32
- **Outcome hit-rate:** 59% (predicted W/D/L matched actual)
- **Mean probability on the actual outcome:** 0.43 · **Brier score:** 0.551 (lower is better)
- **Total-goals mean abs error:** 1.44 goals/match

> Read these as a small-sample sanity check (one matchday), not a verdict. Blowouts like Germany 7-1 and Canada 6-0 inflate the goals error — the model is calibrated to typical scorelines, not outliers.

## Backtest — prediction vs actual (played)

| Date | Fixture | Pred xG | Likely | P(H/D/A) | Actual | ✓ |
|---|---|---|---|---|---|:--:|
| 2026-06-11 | Mexico v South Africa | 1.6-0.8 | 1-0 | 54%/25%/20% | **2-0** | ✅ |
| 2026-06-11 | South Korea v Czechia | 1.3-1.5 | 1-1 | 34%/25%/41% | **2-1** | — |
| 2026-06-12 | Canada v Bosnia-Herzegovina | 1.8-0.9 | 1-0 | 57%/23%/19% | **1-1** | — |
| 2026-06-12 | United States v Paraguay | 1.3-1.0 | 1-1 | 41%/28%/31% | **4-1** | ✅ |
| 2026-06-13 | Qatar v Switzerland | 1.0-2.3 | 1-2 | 16%/19%/65% | **1-1** | — |
| 2026-06-13 | Brazil v Morocco | 1.5-1.0 | 1-0 | 48%/26%/26% | **1-1** | — |
| 2026-06-13 | Haiti v Scotland | 0.7-1.6 | 0-1 | 16%/25%/59% | **0-1** | ✅ |
| 2026-06-13 | Australia v Türkiye | 1.3-1.1 | 1-1 | 40%/28%/32% | **2-0** | ✅ |
| 2026-06-14 | Sweden v Tunisia | 1.1-1.2 | 1-1 | 34%/28%/38% | **5-1** | — |
| 2026-06-14 | Netherlands v Japan | 1.2-1.1 | 1-1 | 38%/28%/35% | **2-2** | — |
| 2026-06-14 | Germany v Curaçao | 3.5-0.8 | 3-0 | 84%/10%/6% | **7-1** | ✅ |
| 2026-06-14 | Ivory Coast v Ecuador | 0.7-0.8 | 0-0 | 28%/38%/34% | **1-0** | — |
| 2026-06-15 | Belgium v Egypt | 1.8-0.8 | 1-0 | 60%/23%/17% | **1-1** | — |
| 2026-06-15 | Iran v New Zealand | 1.1-0.8 | 1-0 | 42%/31%/27% | **2-2** | — |
| 2026-06-15 | Spain v Cape Verde | 2.0-0.6 | 1-0 | 69%/20%/11% | **0-0** | — |
| 2026-06-15 | Saudi Arabia v Uruguay | 0.5-1.2 | 0-1 | 16%/30%/53% | **1-1** | — |
| 2026-06-16 | Austria v Jordan | 2.0-0.6 | 1-0 | 70%/20%/10% | **3-1** | ✅ |
| 2026-06-16 | Argentina v Algeria | 1.6-0.9 | 1-0 | 54%/25%/21% | **3-0** | ✅ |
| 2026-06-16 | France v Senegal | 1.6-0.8 | 1-0 | 58%/24%/18% | **3-1** | ✅ |
| 2026-06-16 | Iraq v Norway | 0.9-1.3 | 0-1 | 25%/28%/47% | **1-4** | ✅ |
| 2026-06-17 | Portugal v Congo DR | 1.8-0.6 | 1-0 | 64%/23%/13% | **1-1** | — |
| 2026-06-17 | Uzbekistan v Colombia | 0.5-1.6 | 0-1 | 12%/25%/63% | **1-3** | ✅ |
| 2026-06-17 | England v Croatia | 1.1-1.1 | 1-1 | 36%/28%/36% | **4-2** | ✅ |
| 2026-06-17 | Ghana v Panama | 1.3-1.0 | 1-0 | 44%/28%/28% | **1-0** | ✅ |
| 2026-06-18 | Czechia v South Africa | 1.2-1.0 | 1-0 | 42%/29%/29% | **1-1** | — |
| 2026-06-18 | Mexico v South Korea | 1.9-1.1 | 1-1 | 54%/23%/24% | **1-0** | ✅ |
| 2026-06-18 | Switzerland v Bosnia-Herzegovina | 2.1-1.0 | 1-0 | 61%/21%/18% | **4-1** | ✅ |
| 2026-06-18 | Canada v Qatar | 2.0-0.9 | 1-0 | 62%/21%/17% | **6-0** | ✅ |
| 2026-06-19 | Türkiye v Paraguay | 1.0-1.2 | 1-1 | 31%/28%/41% | **0-1** | ✅ |
| 2026-06-19 | Scotland v Morocco | 0.9-1.3 | 0-1 | 27%/28%/46% | **0-1** | ✅ |
| 2026-06-19 | Brazil v Haiti | 2.5-0.5 | 2-0 | 79%/14%/6% | **3-0** | ✅ |
| 2026-06-19 | United States v Australia | 1.3-1.1 | 1-1 | 43%/27%/30% | **2-0** | ✅ |

## Forecast — next fixtures (with momentum nudge)

_`Mom` = recency-weighted form (+ scouted sentiment) applied as a small, capped log-rate nudge to each side's goals (home/away)._

| Date | Fixture | Pred xG | Likely | P(H/D/A) | Over 2.5 | Mom H/A |
|---|---|---|---|---|---|---|
| 2026-06-20 | Netherlands v Sweden | 2.0-1.2 | 1-1 | 55%/21%/24% | 62% | +0.02/+0.04 |
| 2026-06-20 | Tunisia v Japan | 0.6-1.1 | 0-1 | 21%/32%/47% | 26% | -0.13/+0.05 |
| 2026-06-20 | Germany v Ivory Coast | 1.9-1.3 | 1-1 | 51%/22%/26% | 60% | +0.18/+0.10 |
| 2026-06-20 | Ecuador v Curaçao | 1.8-0.4 | 1-0 | 70%/22%/8% | 36% | +0.02/-0.18 |
| 2026-06-21 | Belgium v Iran | 2.2-0.8 | 2-0 | 70%/18%/12% | 57% | +0.18/+0.00 |
| 2026-06-21 | New Zealand v Egypt | 0.7-1.2 | 0-1 | 22%/31%/47% | 28% | -0.12/+0.01 |
| 2026-06-21 | Spain v Saudi Arabia | 1.6-0.6 | 1-0 | 62%/25%/14% | 38% | +0.04/-0.06 |
| 2026-06-21 | Uruguay v Cape Verde | 1.6-0.5 | 1-0 | 61%/26%/13% | 34% | -0.03/+0.01 |
| 2026-06-22 | France v Iraq | 2.0-0.5 | 1-0 | 73%/19%/8% | 44% | +0.08/-0.12 |
| 2026-06-22 | Norway v Senegal | 1.3-1.2 | 1-1 | 39%/27%/34% | 45% | +0.09/-0.07 |
| 2026-06-22 | Argentina v Austria | 1.8-1.1 | 1-1 | 52%/23%/25% | 54% | +0.18/+0.16 |
| 2026-06-22 | Jordan v Algeria | 0.6-1.9 | 0-1 | 11%/21%/68% | 44% | -0.10/-0.01 |
| 2026-06-23 | Portugal v Uzbekistan | 1.9-0.4 | 1-0 | 72%/20%/8% | 42% | +0.06/-0.09 |
| 2026-06-23 | Colombia v Congo DR | 1.7-0.7 | 1-0 | 61%/24%/15% | 40% | +0.09/-0.02 |
| 2026-06-23 | England v Ghana | 2.2-0.8 | 2-0 | 70%/18%/12% | 56% | +0.06/-0.11 |
| 2026-06-23 | Panama v Croatia | 0.5-1.6 | 0-1 | 11%/24%/64% | 36% | -0.08/-0.09 |
| 2026-06-24 | Morocco v Haiti | 1.8-0.5 | 1-0 | 68%/22%/10% | 39% | +0.07/-0.03 |
| 2026-06-24 | Bosnia-Herzegovina v Qatar | 1.6-1.3 | 1-1 | 44%/25%/32% | 54% | -0.08/-0.18 |
| 2026-06-24 | Scotland v Brazil | 1.0-2.4 | 1-2 | 16%/18%/66% | 65% | +0.04/+0.14 |
| 2026-06-24 | South Africa v South Korea | 0.9-1.1 | 0-1 | 31%/30%/39% | 33% | -0.07/-0.05 |
| 2026-06-24 | Mexico v Czechia | 1.9-1.2 | 1-1 | 55%/22%/23% | 59% | +0.09/-0.04 |
| 2026-06-24 | Canada v Switzerland | 1.4-1.4 | 1-1 | 38%/25%/37% | 53% | +0.15/+0.12 |

## Squad & player context (forecast teams)

_From real player data: squad rating, average age (seniority), stylistic tilt, and talisman._

| Team | Tier | Squad ovr | Avg age | Style | Talisman |
|---|---|---|---|---|---|
| Netherlands | Elite contender | 83.0 | 27.4 | well-balanced | V. van Dijk |
| Tunisia | Developing team | 70.9 | 27.2 | attack-leaning | E. Skhiri |
| Germany | Elite contender | 85.9 | 28.6 | attack-leaning | J. Kimmich |
| Ecuador | Developing team | 73.9 | 28.3 | attack-leaning | P. Estupiñán |
| Belgium | Elite contender | 83.8 | 29.7 | attack-leaning | K. De Bruyne |
| New Zealand | Developing team | 68.8 | 26.2 | well-balanced | C. Wood |
| Spain | Elite contender | 85.5 | 30.4 | well-balanced | Sergio Ramos |
| Uruguay | Strong side | 80.9 | 29.4 | well-balanced | L. Suárez |
| France | Elite contender | 85.6 | 27.3 | attack-leaning | K. Mbappé |
| Norway | Solid outfit | 76.8 | 26.1 | attack-leaning | E. Haaland |
| Argentina | Elite contender | 84.4 | 29.0 | attack-leaning | L. Messi |
| Jordan | Developing team | 64.3 | 26.7 | attack-leaning | M. Al-Tamari |
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
| Sweden | Solid outfit | 77.5 | 28.4 | attack-leaning | Z. Ibrahimović |
| Japan | Developing team | 75.5 | 28.2 | attack-leaning | D. Kamada |
| Ivory Coast | Solid outfit | 78.0 | 27.9 | attack-leaning | F. Kessié |
| Curaçao | Developing team | 67.5 | 27.7 | attack-leaning | J. Bacuna |
| Iran | Developing team | 70.9 | 28.2 | well-balanced | M. Taremi |
| Egypt | Developing team | 72.2 | 25.6 | attack-leaning | M. Salah |
| Saudi Arabia | Developing team | 70.8 | 27.8 | well-balanced | S. Al Dawsari |
| Cape Verde | Developing team | 70.8 | 27.9 | attack-leaning | Jovane Cabral |
| Iraq | Developing team | 66.5 | 29.8 | attack-leaning | A. Yasin |
| Senegal | Solid outfit | 78.8 | 27.7 | well-balanced | S. Mané |
| Austria | Solid outfit | 78.9 | 27.8 | well-balanced | D. Alaba |
| Algeria | Solid outfit | 77.9 | 27.9 | attack-leaning | R. Mahrez |
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