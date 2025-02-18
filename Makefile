test:
	pytest -vv --cov dokli --blockage

format:
	ruff format dokli/
	ruff check dokli/ --fix-only

lint:
	ruff check dokli/
	mypy dokli

dev-tui:
	textual run --dev dokli.tui.app:DokliApp

def-tui-console:
	textual console - SYSTEM -X EVENT
