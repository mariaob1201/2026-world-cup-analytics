.PHONY: setup data features fit simulate all test clean

# Overridable: locally defaults to the project venv; CI passes PY=python.
PY ?= .venv/bin/python

setup:
	python3 -m venv .venv
	$(PY) -m pip install --upgrade pip
	$(PY) -m pip install -r requirements.txt
	$(PY) -m pip install -e .

data:
	$(PY) scripts/01_generate_data.py

features:
	$(PY) scripts/02_build_features.py

fit:
	$(PY) scripts/03_fit_model.py

simulate:
	$(PY) scripts/04_simulate_tournament.py

# Full synthetic demo pipeline, in order.
all: data features fit simulate

# --- Real-data track --------------------------------------------------------
real-players:
	$(PY) scripts/05_extract_real_players.py

real-fit:
	$(PY) scripts/06_fit_real.py

mexico:
	$(PY) scripts/07_assess_mexico.py

card:
	$(PY) scripts/09_social_card.py --handle $(HANDLE)
HANDLE ?= @your_handle

# Real player data -> real-match fit -> Mexico assessment.
real: real-players real-fit mexico

elo:
	$(PY) scripts/10_elo.py

simulate-real:
	$(PY) scripts/15_simulate_real.py

champion:
	$(PY) scripts/16_champion_tracker.py

# Knockout opponent odds for a team (default Mexico R32 at the Azteca).
r32-odds:
	$(PY) scripts/23_r32_odds.py $(ARGS)

# Fetch real current squads from Wikipedia (fixes vintage rosters).
live-squads:
	$(PY) scripts/17_live_squads.py

# Build the model prior from the real current squads (real names/caps/age).
live-features:
	$(PY) scripts/18_live_features.py

# Backtest the model vs Elo + naive baselines across 2018/2022/2026 (the scoreboard).
evaluate:
	$(PY) scripts/19_evaluate.py

prediction-log:
	$(PY) scripts/20_prediction_log.py

# Harvest real World Cup xG (StatsBomb open data) -> data/raw/xg_matches.csv.
fetch-xg:
	$(PY) scripts/22_fetch_statsbomb_xg.py

# Recent-performance form signal (xG/shots) that conditions next-game scores.
form-signal:
	$(PY) scripts/24_form_signal.py $(ARGS)

# Spatial team-style profiles from StatsBomb x,y (territory, press, shot location).
spatial:
	$(PY) scripts/25_spatial.py $(ARGS)

# Simulation-Based Inference demo: rejection-ABC vs truth vs exact MCMC.
sbi-demo:
	$(PY) scripts/26_sbi_abc.py

# Build tabular datasets: per-player attributes + per-team assessment (results +
# model ratings + aggregated player characteristics).
dataset:
	$(PY) scripts/27_build_player_dataset.py

# Winners: next-day match picks + Elo champion scorecard (state-conditioned).
# `make winners ARGS=--llm` adds the LLM-as-a-Judge overlay on the next day.
winners:
	$(PY) scripts/28_predict_winners.py $(ARGS)

# Backtest the xG model vs the goals model (run `make fetch-xg` first;
# `make xg-backtest ARGS=--demo` runs a synthetic sanity check instead).
xg-backtest:
	$(PY) scripts/21_xg_backtest.py $(ARGS)

# The full daily refresh (used by the GitHub Action): real squads + live results
# -> refit -> backtest/forecast -> tracker -> forecast-vs-truth log.
daily: real-players live-squads live-features real-fit elo track champion prediction-log

# Backtest + forecast, then tracking charts/sentiment/tactics. Re-run each matchday.
track:
	$(PY) scripts/13_match_predictions.py
	$(PY) scripts/14_analytics.py

# The living champion tracker: refit on current results, then track. Run each matchday.
track-champion: real-players real-fit champion

# Full real-data pipeline end to end.
real-all: real-players real-fit elo track simulate-real champion mexico

test:
	$(PY) -m pytest

clean:
	rm -rf data/raw/* data/interim/* data/processed/* artifacts/*
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
