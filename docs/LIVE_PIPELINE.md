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
        env: { ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }} }
      - run: |                              # commit refreshed reports + charts
          git config user.name  "tracker-bot"
          git config user.email "bot@users.noreply.github.com"
          git add docs/ artifacts/ data/processed/*.csv
          git commit -m "tracker: refresh $(date -u +%F)" || echo "no change"
          git push
```

The `ANTHROPIC_API_KEY` secret enables the LLM judge/extractor; without it the
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

## Suggested next builds

- Wire `llm_extract` output into `momentum.combined_shifts` (news → goal nudge).
- Swap the player prior to `live_squads` + a current ratings join.
- Add the GitHub Action above and let the tracker self-update.
- Strength-of-schedule / confederation effect (see [METHODOLOGY.md §11](METHODOLOGY.md)).
