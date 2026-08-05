test:
	uv run pytest -vv --cov dokli --blockage

format:
	uv run ruff format dokli/
	uv run ruff check dokli/ --fix-only

lint:
	uv run ruff check dokli/
	uv run mypy dokli

dev-tui:
	uv run textual run --dev dokli.tui.app:DokliApp

def-tui-console:
	uv run textual console - SYSTEM -X EVENT
