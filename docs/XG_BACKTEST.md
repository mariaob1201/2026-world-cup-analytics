# xG & conditioning backtest

_Fit on 102 matches, scored on 26 held-out matches (40 teams), real per-match stats from StatsBomb open data (2018 + 2022 World Cups). Lower RPS/log-loss is better. Conditioning rows nudge the goals model by each team's recent-performance form (as of the day before kickoff — no leakage)._

| Approach | RPS ↓ | log-loss ↓ | hit-rate ↑ | goals MAE ↓ |
|---|---|---|---|---|
| goals model | 0.2319 | 1.0734 | 0.423 | 1.447 |
| xG model (expected goals) | 0.2294 | 1.0554 | 0.577 | 1.394 |
| goals + recent-goals form | 0.2345 | 1.0875 | 0.423 | 1.44 |
| goals + recent-xG form | 0.2255 | 1.0605 | 0.462 | 1.403 |
| goals + recent-SoT form ⭐ | 0.2231 | 1.0549 | 0.5 | 1.453 |
| goals + spatial-style prior (territory/press) | 0.2299 | 1.0688 | 0.385 | 1.364 |

**xG vs goals: -0.0025 RPS → xG WINS — keep it.** **Lowest RPS overall: goals + recent-SoT form.**

xG is a less-noisy measure of chance quality than goals, so abilities learned from it generalize better (a side that created more but lost is rated by what it created). Conditioning the goals model on recent xG/SoT form tests whether 'how recent games went' adds signal. Small test sample — directional, not final. Regenerate with `make xg-backtest` after `make fetch-xg`.

**Live use:** switching the 2026 forecast to xG needs per-match xG for current matches (StatsBomb hasn't released 2026; FBref match-report scraping is the fallback). Until then the live pipeline uses the goals model and this validates xG as the upgrade path.