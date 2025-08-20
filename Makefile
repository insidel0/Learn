# Makefile (put this in the repo root)

PY ?= python
PIP ?= pip
DB ?= learn.db

.PHONY: help install test run ingest fmt lint clean

help:        # show available targets
	@grep -E '^[a-zA-Z_-]+:.*?#' Makefile | awk 'BEGIN {FS=":.*?# "}; {printf "\033[36m%-10s\033[0m %s\n", $$1, $$2}'

install:     # install dependencies
	$(PIP) install -r requirements.txt

test:        # run tests
	pytest -q

run:         # review due cards (CLI)
	$(PY) -m src.learn.cli review

ingest:      # create cards from a file: make ingest FILE=data/sample.txt
	@test -n "$(FILE)" || (echo "Set FILE=path/to/input"; exit 1)
	$(PY) -m src.learn.cli ingest $(FILE)

fmt:         # format (if black installed)
	@black src tests || true

lint:        # lint (if ruff installed)
	@ruff check src tests || true

clean:       # remove caches and DB
	rm -rf .pytest_cache __pycache__ */__pycache__
	rm -f $(DB)

