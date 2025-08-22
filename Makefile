# Makefile

SHELL := /bin/bash

PY ?= python
PIP ?= $(PY) -m pip
BRANCH ?= main
DB ?= learn.db

# Make "learn" importable without installing the package
export PYTHONPATH := src

.PHONY: help install test run ingest fmt lint clean typecheck ship smoke status \
        login _ensure-ssh-dir _ensure-key _known-hosts _ensure-agent _add-key _upload-key _test-ssh

help:        # show available targets
	@grep -E '^[a-zA-Z0-9_-]+:.*?#' Makefile | awk 'BEGIN {FS=":.*?# "}; {printf "\033[36m%-12s\033[0m %s\n", $$1, $$2}'

install:     # install dependencies
	$(PIP) install -r requirements.txt

lint:        # lint (ruff)
	ruff check src tests

fmt:         # format (ruff or black)
	ruff format .
	# black .  # uncomment if you prefer Black instead of Ruff formatter

typecheck:   # mypy on package (uses mypy.ini or pyproject)
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

status:      # compare local vs remote (ahead/behind)
	@git fetch -q origin
	@echo "Branch: $$(git branch --show-current)"
	@git --no-pager status -sb
	@printf "Ahead/behind: "
	@git rev-list --left-right --count @{u}...HEAD
	@echo "Not pushed yet:"; git --no-pager log --oneline @{u}..HEAD || true
	@echo "Missing locally:"; git --no-pager log --oneline HEAD..@{u} || true

# ---------------------------
# GitHub SSH login automation
# ---------------------------

login: _ensure-ssh-dir _ensure-key _known-hosts _ensure-agent _add-key _upload-key _test-ssh  # set up SSH and test GitHub
	@echo "✅ GitHub SSH setup complete."

_ensure-ssh-dir:
	@mkdir -p $$HOME/.ssh
	@chmod 700 $$HOME/.ssh
	@touch $$HOME/.ssh/config
	@chmod 600 $$HOME/.ssh/config

_ensure-key:
	@if [ ! -f $$HOME/.ssh/id_ed25519 ]; then \
		email=$$(git config user.email || echo "you@example.com"); \
		echo "Generating ed25519 SSH key for $$email..."; \
		ssh-keygen -t ed25519 -C "$$email" -f $$HOME/.ssh/id_ed25519 -N ""; \
	else \
		echo "Found existing SSH key: $$HOME/.ssh/id_ed25519"; \
	fi
	@chmod 600 $$HOME/.ssh/id_ed25519
	@chmod 644 $$HOME/.ssh/id_ed25519.pub
	@OS=$$(uname -s); \
	if ! grep -qE '^[[:space:]]*Host[[:space:]]+github\.com$$' $$HOME/.ssh/config 2>/dev/null; then \
		echo "Updating $$HOME/.ssh/config for GitHub..."; \
		{ \
			echo ""; \
			echo "Host github.com"; \
			echo "  HostName github.com"; \
			echo "  User git"; \
			echo "  IdentityFile ~/.ssh/id_ed25519"; \
			echo "  AddKeysToAgent yes"; \
			echo "  IdentitiesOnly yes"; \
			if [ "$$OS" = "Darwin" ]; then echo "  UseKeychain yes"; fi; \
		} >> $$HOME/.ssh/config; \
	fi

_known-hosts:
	@touch $$HOME/.ssh/known_hosts
	@ssh-keygen -F github.com >/dev/null 2>&1 || ssh-keyscan -H github.com >> $$HOME/.ssh/known_hosts

_ensure-agent:
	@if [ -z "$$SSH_AUTH_SOCK" ]; then \
		echo "Starting ssh-agent..."; \
		eval "$$(ssh-agent -s)" >/dev/null; \
		echo $$SSH_AUTH_SOCK > $$HOME/.ssh/.ssh_auth_sock; \
	fi

_add-key:
	@if [ -z "$$SSH_AUTH_SOCK" ] && [ -s $$HOME/.ssh/.ssh_auth_sock ]; then export SSH_AUTH_SOCK=$$(cat $$HOME/.ssh/.ssh_auth_sock); fi; \
	if ! ssh-add -l >/dev/null 2>&1; then \
		OS=$$(uname -s); \
		if [ "$$OS" = "Darwin" ]; then \
			ssh-add --apple-use-keychain $$HOME/.ssh/id_ed25519 || true; \
		else \
			ssh-add $$HOME/.ssh/id_ed25519 || true; \
		fi; \
	else \
		echo "SSH key already loaded in agent."; \
	fi

_upload-key:
	@echo "----------------------------------------------------------------"
	@echo "Your public key (paste into GitHub if needed):"
	@cat $$HOME/.ssh/id_ed25519.pub
	@echo "----------------------------------------------------------------"
	@if command -v gh >/dev/null 2>&1; then \
		if gh auth status >/dev/null 2>&1; then \
			echo "Uploading key to GitHub via gh..."; \
			gh ssh-key add $$HOME/.ssh/id_ed25519.pub -t "learn-$$USER@$$(hostname)-$$(date +%F)" || true; \
		else \
			echo "GitHub CLI installed but not logged in."; \
			echo "Run: gh auth login  (then re-run: make login)"; \
			(command -v xdg-open >/dev/null && xdg-open https://github.com/settings/keys) \
			|| (command -v open >/dev/null && open https://github.com/settings/keys) \
			|| echo "Open https://github.com/settings/keys and paste the key above."; \
		fi; \
	else \
		echo "Tip: install GitHub CLI (gh) for auto-upload, or paste the key above at https://github.com/settings/keys"; \
	fi

_test-ssh:
	@echo "Testing SSH connection to GitHub (this may print a success message and exit non-zero)..."
	@ssh -o StrictHostKeyChecking=no -T git@github.com || true
