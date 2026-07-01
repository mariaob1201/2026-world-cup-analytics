# WC 2026 — Match Predictions vs Reality, and Forecasts

_Model trained on pre-tournament data only (results to 2026-06-10 + FIFA squad prior). Backtest compares those out-of-sample forecasts to the actual scorelines; forecasts cover the next slate. Compiled 2026-07-01._

## Accuracy so far (out-of-sample)

- **Matches scored:** 79
- **Outcome hit-rate:** 62% (predicted W/D/L matched actual)
- **Mean probability on the actual outcome:** 0.45 · **Brier score:** 0.523 (lower is better)
- **Total-goals mean abs error:** 1.44 goals/match

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
| 2026-06-16 | France v Senegal | 1.6-0.8 | 1-0 | 58%/24%/18% | **3-1** | ✅ |
| 2026-06-16 | Iraq v Norway | 0.9-1.3 | 0-1 | 25%/28%/47% | **1-4** | ✅ |
| 2026-06-16 | Argentina v Algeria | 1.6-0.9 | 1-0 | 54%/25%/21% | **3-0** | ✅ |
| 2026-06-17 | Ghana v Panama | 1.3-1.0 | 1-0 | 44%/28%/28% | **1-0** | ✅ |
| 2026-06-17 | England v Croatia | 1.2-1.1 | 1-1 | 36%/28%/36% | **4-2** | ✅ |
| 2026-06-17 | Portugal v Congo DR | 1.8-0.6 | 1-0 | 64%/23%/13% | **1-1** | — |
| 2026-06-17 | Uzbekistan v Colombia | 0.5-1.6 | 0-1 | 12%/25%/63% | **1-3** | ✅ |
| 2026-06-18 | Czechia v South Africa | 1.2-1.0 | 1-0 | 42%/29%/29% | **1-1** | — |
| 2026-06-18 | Mexico v South Korea | 1.9-1.1 | 1-1 | 54%/23%/24% | **1-0** | ✅ |
| 2026-06-18 | Switzerland v Bosnia-Herzegovina | 2.1-1.0 | 1-0 | 61%/21%/18% | **4-1** | ✅ |
| 2026-06-18 | Canada v Qatar | 2.0-0.9 | 1-0 | 62%/21%/17% | **6-0** | ✅ |
| 2026-06-19 | Scotland v Morocco | 0.9-1.3 | 0-1 | 27%/28%/46% | **0-1** | ✅ |
| 2026-06-19 | Brazil v Haiti | 2.5-0.5 | 2-0 | 79%/14%/6% | **3-0** | ✅ |
| 2026-06-19 | United States v Australia | 1.3-1.1 | 1-1 | 42%/27%/30% | **2-0** | ✅ |
| 2026-06-19 | Türkiye v Paraguay | 1.0-1.2 | 1-1 | 31%/28%/40% | **0-1** | ✅ |
| 2026-06-20 | Ecuador v Curaçao | 1.7-0.5 | 1-0 | 68%/23%/10% | **0-0** | — |
| 2026-06-20 | Tunisia v Japan | 0.7-1.1 | 0-1 | 25%/32%/43% | **0-4** | ✅ |
| 2026-06-20 | Germany v Ivory Coast | 1.6-1.1 | 1-1 | 47%/25%/28% | **2-1** | ✅ |
| 2026-06-20 | Netherlands v Sweden | 2.0-1.2 | 1-1 | 55%/22%/23% | **5-1** | ✅ |
| 2026-06-21 | Belgium v Iran | 1.9-0.8 | 1-0 | 62%/22%/16% | **0-0** | — |
| 2026-06-21 | New Zealand v Egypt | 0.8-1.1 | 0-1 | 25%/31%/44% | **1-3** | ✅ |
| 2026-06-21 | Spain v Saudi Arabia | 1.6-0.6 | 1-0 | 59%/26%/15% | **4-0** | ✅ |
| 2026-06-21 | Uruguay v Cape Verde | 1.6-0.5 | 1-0 | 62%/25%/13% | **2-2** | — |
| 2026-06-22 | Argentina v Austria | 1.5-0.9 | 1-0 | 49%/26%/25% | **2-0** | ✅ |
| 2026-06-22 | France v Iraq | 1.8-0.5 | 1-0 | 68%/21%/10% | **3-0** | ✅ |
| 2026-06-22 | Norway v Senegal | 1.2-1.3 | 1-1 | 34%/27%/38% | **3-2** | — |
| 2026-06-22 | Jordan v Algeria | 0.6-1.9 | 0-1 | 12%/21%/66% | **1-2** | ✅ |
| 2026-06-23 | Panama v Croatia | 0.6-1.8 | 0-1 | 11%/22%/67% | **0-1** | ✅ |
| 2026-06-23 | England v Ghana | 2.1-0.8 | 2-0 | 66%/20%/15% | **0-0** | — |
| 2026-06-23 | Colombia v Congo DR | 1.5-0.7 | 1-0 | 57%/26%/17% | **1-0** | ✅ |
| 2026-06-23 | Portugal v Uzbekistan | 1.8-0.5 | 1-0 | 69%/21%/9% | **5-0** | ✅ |
| 2026-06-24 | Mexico v Czechia | 1.8-1.2 | 1-1 | 50%/23%/27% | **3-0** | ✅ |
| 2026-06-24 | South Africa v South Korea | 1.0-1.2 | 0-1 | 31%/29%/39% | **1-0** | — |
| 2026-06-24 | Canada v Switzerland | 1.2-1.2 | 1-1 | 36%/27%/38% | **1-2** | ✅ |
| 2026-06-24 | Bosnia-Herzegovina v Qatar | 1.7-1.5 | 1-1 | 42%/23%/35% | **3-1** | ✅ |
| 2026-06-24 | Scotland v Brazil | 1.0-2.0 | 0-1 | 18%/21%/61% | **0-3** | ✅ |
| 2026-06-24 | Morocco v Haiti | 1.7-0.5 | 1-0 | 65%/24%/11% | **4-2** | ✅ |
| 2026-06-25 | Tunisia v Netherlands | 0.8-1.3 | 0-1 | 24%/28%/47% | **1-3** | ✅ |
| 2026-06-25 | Japan v Sweden | 1.6-1.0 | 1-0 | 51%/25%/24% | **1-1** | — |
| 2026-06-25 | Ecuador v Germany | 0.9-1.1 | 0-1 | 31%/31%/38% | **2-1** | — |
| 2026-06-25 | Paraguay v Australia | 0.9-0.9 | 0-0 | 34%/32%/33% | **0-0** | — |
| 2026-06-25 | United States v Türkiye | 1.8-1.2 | 1-1 | 50%/23%/27% | **2-3** | — |
| 2026-06-25 | Curaçao v Ivory Coast | 0.7-2.2 | 0-2 | 11%/18%/71% | **0-2** | ✅ |
| 2026-06-26 | Egypt v Iran | 1.0-0.9 | 0-0 | 36%/31%/32% | **1-1** | — |
| 2026-06-26 | New Zealand v Belgium | 0.7-2.1 | 0-2 | 10%/19%/71% | **1-5** | ✅ |
| 2026-06-26 | Cape Verde v Saudi Arabia | 0.7-0.9 | 0-0 | 27%/34%/39% | **0-0** | — |
| 2026-06-26 | Uruguay v Spain | 1.1-1.1 | 1-1 | 34%/29%/37% | **0-1** | ✅ |
| 2026-06-26 | Norway v France | 0.8-1.9 | 0-1 | 16%/21%/63% | **1-4** | ✅ |
| 2026-06-26 | Senegal v Iraq | 1.2-0.7 | 1-0 | 47%/30%/23% | **5-0** | ✅ |
| 2026-06-27 | Panama v England | 0.6-2.0 | 0-1 | 11%/20%/70% | **0-2** | ✅ |
| 2026-06-27 | Croatia v Ghana | 1.9-0.8 | 1-0 | 63%/22%/15% | **2-1** | ✅ |
| 2026-06-27 | Congo DR v Uzbekistan | 1.0-0.8 | 0-0 | 41%/33%/26% | **3-1** | ✅ |
| 2026-06-27 | Colombia v Portugal | 1.0-1.2 | 0-1 | 29%/29%/41% | **0-0** | — |
| 2026-06-27 | Jordan v Argentina | 0.5-2.5 | 0-2 | 6%/14%/81% | **1-3** | ✅ |
| 2026-06-27 | Algeria v Austria | 1.1-1.3 | 1-1 | 32%/27%/41% | **3-3** | — |
| 2026-06-28 | South Africa v Canada | 0.8-1.0 | 0-0 | 28%/34%/39% | **0-1** | ✅ |
| 2026-06-29 | Brazil v Japan | 1.5-1.1 | 1-1 | 47%/26%/27% | **2-1** | ✅ |
| 2026-06-29 | Germany v Paraguay | 1.6-1.0 | 1-0 | 51%/25%/24% | **1-1** | — |
| 2026-06-29 | Netherlands v Morocco | 1.2-1.1 | 1-1 | 38%/28%/34% | **1-1** | — |
| 2026-06-30 | Ivory Coast v Norway | 1.3-1.1 | 1-1 | 41%/28%/32% | **1-2** | — |
| 2026-06-30 | France v Sweden | 2.3-0.8 | 2-0 | 69%/18%/13% | **3-0** | ✅ |
| 2026-06-30 | Mexico v Ecuador | 0.9-0.9 | 0-0 | 34%/33%/33% | **2-0** | ✅ |

## Forecast — next fixtures (with momentum nudge)

_`Mom` = recency-weighted form (+ scouted sentiment) applied as a small, capped log-rate nudge to each side's goals (home/away)._

| Date | Fixture | Pred xG | Likely | P(H/D/A) | Over 2.5 | Mom H/A |
|---|---|---|---|---|---|---|
| 2026-07-01 | United States v Bosnia-Herzegovina | 2.2-1.1 | 2-1 | 62%/20%/18% | 62% | +0.03/-0.02 |
| 2026-07-01 | Belgium v Senegal | 1.9-1.0 | 1-0 | 58%/22%/20% | 55% | +0.18/+0.01 |
| 2026-07-01 | England v Congo DR | 1.7-0.8 | 1-0 | 58%/24%/18% | 46% | +0.08/+0.02 |
| 2026-07-02 | Spain v Austria | 1.6-1.2 | 1-1 | 48%/24%/28% | 53% | +0.11/+0.07 |
| 2026-07-02 | Portugal v Croatia | 1.5-0.9 | 1-0 | 51%/26%/22% | 41% | +0.14/-0.02 |
| 2026-07-02 | Switzerland v Algeria | 1.5-1.3 | 1-1 | 41%/25%/34% | 52% | +0.12/+0.02 |
| 2026-07-03 | Australia v Egypt | 1.1-0.9 | 1-0 | 40%/31%/30% | 32% | +0.03/+0.04 |
| 2026-07-03 | Argentina v Cape Verde | 2.4-0.6 | 2-0 | 77%/15%/7% | 56% | +0.18/+0.01 |
| 2026-07-03 | Colombia v Ghana | 2.2-0.6 | 2-0 | 72%/18%/10% | 52% | +0.08/-0.08 |
| 2026-07-04 | Canada v Morocco | 1.1-1.2 | 1-1 | 34%/29%/38% | 39% | +0.11/+0.08 |
| 2026-07-04 | Paraguay v France | 0.6-1.8 | 0-1 | 13%/22%/66% | 45% | -0.04/+0.18 |
| 2026-07-05 | Brazil v Norway | 2.4-1.1 | 2-1 | 65%/18%/17% | 67% | +0.16/+0.05 |

## Squad & player context (forecast teams)

_From real player data: squad rating, average age (seniority), stylistic tilt, and talisman._

| Team | Tier | Squad ovr | Avg age | Style | Talisman |
|---|---|---|---|---|---|
| United States | Developing team | 75.9 | 25.6 | well-balanced | C. Pulisic |
| Belgium | Elite contender | 83.8 | 29.7 | attack-leaning | K. De Bruyne |
| England | Elite contender | 85.1 | 26.7 | attack-leaning | H. Kane |
| Spain | Elite contender | 85.5 | 30.4 | well-balanced | Sergio Ramos |
| Portugal | Elite contender | 84.2 | 27.6 | attack-leaning | Cristiano Ronaldo |
| Switzerland | Strong side | 79.1 | 27.2 | well-balanced | R. Freuler |
| Australia | Developing team | 72.8 | 29.2 | well-balanced | A. Mooy |
| Argentina | Elite contender | 84.4 | 29.0 | attack-leaning | L. Messi |
| Colombia | Strong side | 79.4 | 29.3 | attack-leaning | J. Cuadrado |
| Canada | Developing team | 73.6 | 27.9 | well-balanced | A. Davies |
| Paraguay | Developing team | 74.8 | 29.2 | attack-leaning | C. Ortiz |
| Brazil | Elite contender | 85.4 | 29.9 | well-balanced | Neymar Jr |
| Bosnia-Herzegovina | Developing team | 75.4 | 29.4 | well-balanced | E. Džeko |
| Senegal | Solid outfit | 78.8 | 27.7 | well-balanced | S. Mané |
| Congo DR | Developing team | 74.2 | 28.1 | attack-leaning | C. Bakambu |
| Austria | Solid outfit | 78.9 | 27.8 | well-balanced | D. Alaba |
| Croatia | Strong side | 80.6 | 28.2 | attack-leaning | L. Modrić |
| Algeria | Solid outfit | 77.9 | 27.9 | attack-leaning | R. Mahrez |
| Egypt | Developing team | 72.2 | 25.6 | attack-leaning | M. Salah |
| Cape Verde | Developing team | 70.8 | 27.9 | attack-leaning | Jovane Cabral |
| Ghana | Developing team | 75.8 | 27.0 | well-balanced | T. Partey |
| Morocco | Strong side | 79.2 | 28.8 | well-balanced | A. Hakimi |
| France | Elite contender | 85.6 | 27.3 | attack-leaning | K. Mbappé |
| Norway | Solid outfit | 76.8 | 26.1 | attack-leaning | E. Haaland |

## Notes on method

- **Goals model:** hierarchical Bayesian Poisson — each team's attack/defence fits the data, scorelines are posterior-predictive. See [METHODOLOGY.md](METHODOLOGY.md).
- **Player data** (skillsets, seniority/age, semantic tier) feeds the model's prior and the context table above (FIFA dataset).
- **Public/sentiment sources** (ESPN, SI, social) enrich the Mexico deep-dive ([../data/processed/mexico_assessment.md]) and are wired to extend to other teams via the scouting + X-collector modules.
- **Limitation:** scores are independent Poisson and there is no strength-of-schedule term yet — see METHODOLOGY §10–11.