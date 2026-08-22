SHELL := /bin/bash

.PHONY: format lint check typecheck test ext-test

UV_VERSION ?= 0.12.5
UV_SYNC_ARGS ?= --all-groups --locked


# ── UV rules ───────────────────────────────────────────────────────────────────
install-uv:
	curl -LsSf https://astral.sh/uv/$(UV_VERSION)/install.sh | sh

install-python: install-uv
	uv python install $$(cat .python-version)

# Wrap any target in uv's environment: make uv.lint, make uv.test, ...
uv.%:
	uv run $(UV_RUN_ARGS) $(MAKE) -s $*

# ── Developer rules ────────────────────────────────────────────────────────────
install:
	uv sync $(UV_SYNC_ARGS)

test:
	pytest -vv --cov dokli --blockage

format:
	ruff format dokli/
	ruff check dokli/ --fix-only

lint:
	ruff check dokli/

typecheck:
	ty check dokli/

check: lint typecheck
	ruff format --check dokli/

dev-tui:
	textual run --dev dokli.tui.app:DokliApp

screenshots:
	python tools/screenshots.py

def-tui-console:
	textual console - SYSTEM -X EVENT

release:
	@test -n "$(VERSION)" || (echo "Usage: make release VERSION=0.1.0" && exit 1)
	git tag -a "v$(VERSION)" -m "Release v$(VERSION)"
	git push origin "v$(VERSION)"

step-install: install

step-test: uv.check uv.test
