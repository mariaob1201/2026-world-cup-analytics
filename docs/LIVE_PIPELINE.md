# Keeping It Live — LLMs & Agents to Grow the Repo

How to evolve this from a static analysis into a **self-updating tracker**: pull
live data, extract features with an LLM, refit, and republish the forecast on a
schedule. Each piece below already has a module or a clear hook.

---

## The loop

```
            ┌──────────────────────────────────────────────────────────┐
            │  scheduled agent (daily / per-matchday)                   │
            └──────────────────────────────────────────────────────────┘
   ① INGEST            ② EXTRACT (LLM)        ③ MODEL            ④ PUBLISH
 results (martj42)   match reports / news   refit Bayesian     regenerate
 real squads (wiki)  → structured features  goals model on     CHAMPION_TRACKER
 lineups / news      (injuries, formation,  current results,   + charts, commit
 X / ESPN sentiment  momentum signal)       condition on state to GitHub
```

Every arrow maps to code that exists:

| Step | Module / stage | Status |
|---|---|---|
| ① results | `data/sources.py: build_real_matches` | live (martj42, auto-updates) |
| ① **real squads** | `data/live_squads.py` (stage 17) | live (Wikipedia call-ups — fixes vintage names) |
| ① sentiment | `data/x_collector.py` (stage 08), `data/scouting.py` | X = budget-capped; scouting = manual/LLM |
| ② **LLM feature extraction** | `models/llm_extract.py` | scaffold (Claude structured output) |
| ② LLM judge (per fixture) | `models/llm_judge.py` (stage 11) | live (Claude + Elo fallback) |
| ③ refit + condition on state | stage 06 + `simulate_tournament(played=…)` (stage 16) | live |
| ④ publish | stages 13–16 write `docs/*.md` + `artifacts/*.png` | live |

---

## Where LLMs/agents actually help

1. **Feature extraction from unstructured text** (`llm_extract.py`). Feed a match
   report or preview; Claude returns `{formation, injuries, suspensions,
   likely_xi_changes, momentum_signal}`. `momentum_from_features()` maps the
   signal to the same capped goal-rate nudge the model already accepts — so a
   "key striker injured" line nudges that team's attack down. This is the bridge
   from *news* to *numbers*.

2. **Per-fixture judgment** (`llm_judge.py`). Claude fuses Elo + Bayesian
   strength + form + tactics + sentiment into a calibrated 1X2 + rationale for a
   specific match — a qualitative cross-check on the formula.

3. **Narrative generation.** The report `_render` functions are templated today;
   an LLM can write the prose ("why these odds moved") from the structured
   tables, keeping voice consistent as data updates.

4. **Orchestration agent.** A scheduled agent runs the loop, decides *what
   changed* (new results? new lineups?), reruns only what's needed, and commits.

---

## Two ways to run it on a schedule

**A. GitHub Actions (no server).** Add `.github/workflows/track.yml`:

```yaml
name: champion-tracker
on:
  schedule: [{ cron: "0 12 * * *" }]   # daily 12:00 UTC
  workflow_dispatch: {}
jobs:
  track:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - run: pip install -r requirements.txt && pip install -e .
      - run: make track-champion           # fetch → refit → regenerate tracker
        env:                                # set whichever LLM key you have
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
      - run: |                              # commit refreshed reports + charts
          git config user.name  "tracker-bot"
          git config user.email "bot@users.noreply.github.com"
          git add docs/ artifacts/ data/processed/*.csv
          git commit -m "tracker: refresh $(date -u +%F)" || echo "no change"
          git push
```

Either LLM key (`OPENAI_API_KEY` or `ANTHROPIC_API_KEY`) enables the judge/
extractor — the code auto-detects the provider; without a key the deterministic
fallbacks run and the loop still works.

**B. A Claude Code scheduled agent** (the `/schedule` skill) running
`make track-champion` on a cron — same effect, plus the agent can summarize the
day's movement in the commit message or a Slack post.

---

## To make squads fully real (the C. Vela fix)

`live_squads.py` already pulls the real roster (name, position, **age**, **caps**,
club). The one missing piece is **skill ratings** — Wikipedia doesn't carry them.
Close it with `merge_skills(real_squad, current_fc_ratings)`: drop in a CURRENT
EA FC (FC24/FC25) ratings table and join by name. Then the prior is built from
*real players with current skills*, not a stale snapshot. Until then, use
`live_squads` for who-plays + seniority and treat FIFA skills as optional.

---

## Per-match data: lineups, ratings, timeline (and the Google-panel question)

Wanting *team stats, lineups, player ratings, and the match timeline* per game is
reasonable — here's what's actually usable:

| Want | Usable source | Note |
|---|---|---|
| Lineups, formation, subs, cards, goal timeline | **ESPN hidden JSON** (`site.api.espn.com/.../summary?event=<id>`) or the match's Wikipedia report | Structured, free; the right primary feed |
| Team match stats (shots, possession, xG) | ESPN summary endpoint; FBref via `soccerdata` | |
| Player performance ratings | a current **EA FC** dataset (pre-match quality); post-match ratings (SofaScore/WhoScored) are paywalled/ToS-restricted | |
| Semantic timeline / narrative | feed the match report into **`models/llm_extract.py`** → structured `{formation, injuries, momentum_signal}` | LLM turns prose → features |

**On the Google search panel** (the link you shared): that match card is **not an
API** — scraping Google results is brittle and against its ToS, so don't build on
it. Use the sports-data feeds above (ESPN/FBref/Wikipedia) for the same lineups,
stats, and timeline in a stable, structured form, and let the LLM extractor read
any free-text report for the semantic layer.

**The daily forecast-vs-truth ledger** ([FORECAST_LOG.md](FORECAST_LOG.md), stage
20) is the payoff: every goal forecast is recorded before kickoff and scored
against the real result, so accuracy (hit-rate, goals MAE, RPS) accumulates as the
tournament runs — `make prediction-log`, refreshed daily by `.github/workflows/track.yml`.

## Conditioning the next score on recent performance (not just results)

`models/momentum.performance_form(stats, asof, metric="xg")` turns a per-match
stats table into a recency-weighted **form nudge** from a *deeper* metric than
goals — recent **xG** (or shots-on-target) for−against. A side that has been
creating more than it concedes is bumped up even if the scoreline hasn't caught
up. It returns the same `{team: shift}` dict the goal-based momentum does, so it
drops straight into the score forecast:

```python
shifts = performance_form(stats, asof="2026-06-24", metric="xg")
predict_match(idata, teams, home, away, shifts=shifts)   # next score, conditioned
```

`make form-signal` shows it on real StatsBomb xG (e.g. mid-2018 it flags
Brazil/Belgium/Spain in-form, Panama/Costa Rica cold). **Live 2026 caveat:** this
needs a per-match xG/shots feed; until 2026 xG is available it falls back to the
goal-based momentum already wired into the tracker.

## Exploratory "spice" features

Two extra feature families, to enrich the team profile / condition predictions.
Both are **opt-in and unproven** — add as covariates and keep only what lowers
RPS on the [scoreboard](EVALUATION.md).

- **Spatial style** (`data/statsbomb.team_spatial_profiles`, `make spatial`) —
  from StatsBomb x,y event locations: `territory` (how high a team plays),
  `press_height` (defensive actions in the attacking half), `box_share` and
  `shot_dist` (shot quality by location). Real, data-backed: 2022 flags
  Germany/Spain as high-press, Brazil/France as most territorial, Poland with the
  best shot locations.
- **Social/semantic sentiment** (`features/sentiment.py`) — runs per-team
  social/news text through the LLM extractor → a sentiment score → a small capped
  goal-rate nudge. You supply the text (X collector, news); no key → neutral.

> Caveat: sentiment is weak/noisy and spatial features are stylistic, not
> outcomes — they're "spice", validated on RPS before they earn a place. And both
> need a live per-match/per-team feed for 2026 (StatsBomb hasn't released it).

## Suggested next builds

- Wire `llm_extract` output into `momentum.combined_shifts` (news → goal nudge).
- Swap the player prior to `live_squads` + a current ratings join.
- Add the GitHub Action above and let the tracker self-update.
- Strength-of-schedule / confederation effect (see [METHODOLOGY.md §11](METHODOLOGY.md)).
