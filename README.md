# World Cup 2026 Analytics — Bayesian Winner Prediction

Per-player analytics (longevity, position, skills, social reach) feeding a
**hierarchical Bayesian score model** that simulates the 48-team tournament and
outputs each nation's probability of winning.

This README doubles as a walkthrough of *how to structure a project around a
Bayesian model* — read the "Mental model" section if that's your main goal.

---

## Quick start

```bash
make setup      # create .venv and install deps (PyMC, ArviZ, pandas, …)
make all        # run the full pipeline: data → features → fit → simulate
make test       # fast smoke tests (tiny sampler, runs in seconds)
```

Or step by step:

```bash
make data       # 01: generate synthetic players + matches + fixtures → data/raw/
make features   # 02: engineer player features + per-team prior  → data/processed/
make fit        # 03: sample the posterior (NUTS)                 → artifacts/posterior.nc
make simulate   # 04: Monte-Carlo the bracket                     → artifacts/champion_probs.png
```

**Real player data + semantic profiles** (stage 05, separate from the synthetic demo):

```bash
.venv/bin/python scripts/05_extract_real_players.py
```

Downloads a public ~19k-player dataset (sofifa/FIFA schema), builds each
nation's squad by nationality, engineers the same features, and writes a
human-readable report to `data/processed/team_profiles.md` plus structured
`team_interpretation.csv`. See "Real player data & semantic interpretation".

**Fully real pipeline + Mexico deep-dive** (real matches + real priors + tactics):

```bash
make real    # 05 real squads → 06 fit on real intl results → 07 Mexico assessment
```

- Stage 06 fits the model on **real international results** (martj42 dataset,
  2022–present) instead of synthetic matches → `posterior_strength_real.csv`.
- Stage 07 produces `data/processed/mexico_assessment.md`: Bayesian strength
  rank, real squad profile, **formation analysis** (4-4-2 vs 4-3-3 vs the
  scouted 4-1-4-1), recent form, key players, and a **media + X/social sentiment**
  layer — with public-source citations encoded in
  [`data/scouting.py`](src/wc2026/data/scouting.py).

### Optional: live X (Twitter) sentiment

X moved to **pay-per-use** in 2026 (~$0.005/post read, with a one-time $10
credit for migrated accounts), so a small test is cheap — a 100-post pull is
~$0.50. [`scripts/08_collect_x.py`](scripts/08_collect_x.py) is budget-safe:
hard-capped at 100 posts/run, prints a cost estimate, and has a `--probe` mode
that confirms your key for pennies.

```bash
pip install tweepy
export X_BEARER_TOKEN="AAAA..."
python scripts/08_collect_x.py --probe                  # ~$0.06 auth+read test
python scripts/08_collect_x.py --query "Mexico World Cup" --max 50 --lang en
```

It saves to `data/raw/x_<query>.json`; stage 07 auto-detects that file and folds
the live sentiment into the Mexico report. The sentiment scorer
([`data/x_collector.py`](src/wc2026/data/x_collector.py)) is a transparent
lexicon by default — swap `score_text` for a model (HF transformers or the
Claude API) for production accuracy.

> **Data note.** Ships with a *synthetic* data generator so the whole pipeline
> runs offline. Each generator function in `src/wc2026/data/generate_synthetic.py`
> is an isolated adapter — replace its body with a real source (FBref/StatsBomb
> open data, FIFA rankings, an X/Instagram API for social) returning the same
> columns, and nothing downstream changes.

---

## The mental model: how a Bayesian project is laid out

A Bayesian analysis is always the same four moves. This repo maps one directory
/ stage to each, which is the pattern you can reuse for any Bayesian project:

| Bayesian step | Question it answers | Where it lives |
|---|---|---|
| **1. Data** | What did we observe? | `data/` + `data/generate_synthetic.py` |
| **2. Model** | How do unknown *parameters* generate that data? | `models/bayesian_score.py` |
| **3. Inference** | Given the data, what do we now believe about the parameters? | `scripts/03_fit_model.py` (NUTS sampling) |
| **4. Prediction** | What does that belief imply about the future? | `models/simulate.py` |

The defining feature of the Bayesian approach: **every unknown is a probability
distribution, not a single number.** We never say "Brazil's attack strength is
0.9"; we carry a whole posterior distribution over it and let that uncertainty
flow all the way through to the final "Brazil wins with p%".

### 1. Prior → 2. Likelihood → 3. Posterior

Bayes' rule in one line:

```
posterior  ∝  likelihood × prior
P(params | data)  ∝  P(data | params) × P(params)
```

- **Prior** `P(params)` — what we believe *before* seeing match results. This is
  where your player analytics enter: a squad with better players is *a priori*
  expected to attack better (see `beta_prior` below).
- **Likelihood** `P(data | params)` — the generative story for the data. Here:
  goals are Poisson counts whose rate depends on the teams' attack/defence.
- **Posterior** `P(params | data)` — updated beliefs after seeing the matches.
  We can't write it in closed form, so we **sample** from it with MCMC (NUTS).

---

## The model

For a match between home team `h` and away team `a`:

```
home_goals ~ Poisson(λ_home)
away_goals ~ Poisson(λ_away)

log λ_home = intercept + home_adv + att_eff[h] − def[a]
log λ_away = intercept           + att_eff[a] − def[h]
```

Each team has an **attack** and a **defence** ability. Key design choices:

- **Partial pooling (the "hierarchical" part).** `att`/`def` are drawn from a
  shared distribution whose spread `σ` is *itself* estimated:
  `att[t] ~ ZeroSumNormal(σ_att)`. Teams with few games get pulled toward the
  average; teams with many games keep their own signal. This is the Bayesian
  fix for small samples and the reason it beats fitting 48 independent ratings.
- **Player analytics as an informed prior.** The attack ability is centred on
  the `prior_strength` covariate engineered from player skills/longevity/social
  reach: `att_eff = att + beta_prior · prior_strength`. `beta_prior` is itself a
  parameter, so **the model learns how much to trust your covariate** rather than
  you hard-coding its influence.
- **Identifiability.** Abilities are only defined up to a constant, so we use
  zero-sum (`ZeroSumNormal`) parameters and let `intercept` absorb the overall
  scoring level.

See the docstring of [`bayesian_score.py`](src/wc2026/models/bayesian_score.py)
for the full annotated model.

### Inference & checking it worked

`scripts/03_fit_model.py` runs NUTS (4 chains) and prints an ArviZ summary.
**Always check convergence before trusting results:**

- **R-hat ≈ 1.00** for every parameter (compares within- vs between-chain
  variance; >1.01 means chains disagree → sample more / reparametrize).
- **ESS** (effective sample size) in the hundreds+.
- No divergences (raise `target_accept` toward 0.95–0.99 if you see them).

### From posterior to prediction (the Bayesian payoff)

`scripts/04_simulate_tournament.py` runs ~5000 Monte-Carlo tournaments. On
**each** simulated tournament it draws a *fresh* parameter set from the
posterior — so some tournaments use a draw where Brazil looks elite, others a
draw where Brazil is merely good. Aggregating across all of them propagates
**parameter uncertainty** into the headline probabilities. A point-estimate
simulation cannot do this; it would understate how uncertain the prediction is.

The 2026 format is implemented faithfully: 12 groups of 4 → top 2 + 8 best
third-placed teams → Round of 32 → single elimination.

---

## Per-player features

Built in [`features/player_features.py`](src/wc2026/features/player_features.py):

| Feature | Definition |
|---|---|
| **longevity** | standardized blend of career length (age − debut age) and international caps |
| **position** | `GK/DF/MF/FW`, kept categorical and one-hot encoded |
| **skill_index** | weighted blend of pace/shooting/passing/dribbling/defending/physical |
| **social_score** | log₁₀(followers) modulated by engagement rate, standardized |
| **star_power** | the single biggest social name in the squad |

These roll up (top-16-by-overall per nation) into the per-team
`prior_strength` covariate that informs the model.

---

## Real player data & semantic interpretation

`scripts/05_extract_real_players.py` pulls a real, openly-hosted player dataset
([`data/sources.py`](src/wc2026/data/sources.py)) and builds national squads by
nationality (top-26 by overall). It maps 1:1 onto the project's schema, so the
same feature pipeline runs on it.

On top of the numbers, [`features/interpretation.py`](src/wc2026/features/interpretation.py)
adds a **rule-based semantic layer** — transparent, auditable, no black box:

- **Per player** → an archetype: *Clinical finisher, Creative hub, Ball-playing
  defender, Veteran talisman, Star prospect, …* (from position + age + standout skills).
- **Per team** → a structured profile + one-paragraph narrative: quality **tier**,
  **age profile** (youthful / balanced / veteran-heavy), stylistic **tilt** (attack
  vs defence), squad **depth** (deep vs top-heavy), and **star power**.

Example output:

> *France profile as an elite contender (avg top-16 rating 85.6). The squad is
> balanced age (mean 27.1) and attack-leaning, with moderate depth. Talisman:
> K. Mbappé (91 ovr), giving galactico-level star power.*

**Documented proxies** (the source lacks these fields): `longevity` is proxied
from age + international reputation; `social_score`/`followers` from
international reputation (follower APIs are paid). Vintage is FIFA 22, and squads
are a nationality pool, not the official call-ups — see the module docstrings.

## Project layout

```
src/wc2026/
  config.py              paths, seed, sizing constants
  data/
    teams.py             48 teams, 12 groups, latent strengths (synthetic truth)
    generate_synthetic.py  players / matches / fixtures generators (swap for real)
  features/
    player_features.py   per-player features + team rollup → prior_strength
  models/
    bayesian_score.py    PyMC hierarchical Poisson model + fit()
    simulate.py          Monte-Carlo tournament from posterior draws
  viz/plots.py           strength scatter + title-probability bar chart
scripts/                 01→04 pipeline (thin wrappers over src/)
tests/test_smoke.py      shapes, features, tiny end-to-end fit
artifacts/               posterior.nc + PNGs (gitignored)
```

## Extending to real data

1. **Matches** — point `generate_matches` at a results feed (qualifiers +
   friendlies). The model only needs `home_team, away_team, home_goals, away_goals`.
2. **Players & social** — replace `generate_players` with FBref/Transfermarkt
   scrapes + an X/Instagram API. Keep the column names and features flow through.
3. **Groups** — replace the `latent_strength` table in `teams.py` with the real
   drawn groups once announced; drop the synthetic-truth column.
4. **Official bracket** — swap `_seed_bracket` in `simulate.py` for the official
   R32 crossing table.

## Caveats (it's a teaching model, read these)

- Synthetic data means the *numbers are illustrative, not forecasts.*
- Goals are modelled as **independent** Poisson; reality has mild correlation
  (a bivariate-Poisson / Dixon-Coles correction is a natural upgrade).
- Squad strength is static — no in-tournament form, injuries, or fatigue.
- Social media is a weak causal signal for results; it's included because you
  asked for it and as a demo of folding soft features into a prior — keep its
  prior weight modest.
