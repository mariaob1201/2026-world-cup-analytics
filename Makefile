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

test:
	$(PY) -m pytest

clean:
	rm -rf data/raw/* data/interim/* data/processed/* artifacts/*
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
