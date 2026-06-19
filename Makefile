.PHONY: setup data features fit simulate all test clean

PY := .venv/bin/python

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

# Fetch real current squads from Wikipedia (fixes vintage rosters).
live-squads:
	$(PY) scripts/17_live_squads.py

# Backtest the model vs Elo + naive baselines across 2018/2022/2026 (the scoreboard).
evaluate:
	$(PY) scripts/19_evaluate.py

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
