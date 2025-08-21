# Makefile

PY ?= python
PIP ?= $(PY) -m pip
BRANCH ?= main
DB ?= learn.db

# Make "learn" importable without installing the package
export PYTHONPATH := src

.PHONY: help install test run ingest fmt lint clean typecheck ship smoke

help:        # show available targets
	@grep -E '^[a-zA-Z_-]+:.*?#' Makefile | awk 'BEGIN {FS=":.*?# "}; {printf "\033[36m%-10s\033[0m %s\n", $$1, $$2}'

install:     # install dependencies
	$(PIP) install -r requirements.txt

lint:        # lint (ruff)
	ruff check src tests

fmt:         # format (ruff or black)
	ruff format .
	# black .  # uncomment if you prefer Black instead of Ruff formatter

typecheck:   # mypy on package (uses mypy.ini)
	mypy -p learn

test:        # run tests
	pytest -q

run:         # review due cards (CLI)
	$(PY) -m learn.cli review

ingest:      # create cards from a file: make ingest FILE=data/sample.txt
	@test -n "$(FILE)" || (echo "Set FILE=path/to/input"; exit 1)
	$(PY) -m learn.cli ingest $(FILE)

smoke:       # non-interactive CLI smoke test
	mkdir -p data
	printf "Long paragraph about spaced repetition etc.\n\nAnother paragraph about Pomodoro." > data/sample.txt
	$(PY) -m learn.cli ingest data/sample.txt
	printf "\n4\n" | $(PY) -m learn.cli review

clean:       # remove caches and DB
	rm -rf .pytest_cache .mypy_cache .ruff_cache __pycache__ */__pycache__
	rm -f $(DB) coverage.xml

ship: lint typecheck test  # run all checks, then commit & push
	@test -n "$(MSG)" || (echo "Usage: make ship MSG='your message'"; exit 1)
	git add -A
	-git commit -m "$(MSG)"
	git push origin HEAD:$(BRANCH)

status:  # compare local vs remote (ahead/behind)
	@git fetch -q origin
	@echo "Branch: $$(git branch --show-current)"
	@git --no-pager status -sb
	@echo -n "Ahead/behind: "; git rev-list --left-right --count @{u}...HEAD
	@echo "Not pushed yet:"; git --no-pager log --oneline @{u}..HEAD || true
	@echo "Missing locally:"; git --no-pager log --oneline HEAD..@{u} || true
