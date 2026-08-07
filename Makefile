test:
	uv run pytest -vv --cov dokli --blockage

format:
	uv run ruff format dokli/
	uv run ruff check dokli/ --fix-only

lint:
	uv run ruff check dokli/
	uv run ty check dokli

dev-tui:
	uv run textual run --dev dokli.tui.app:DokliApp

def-tui-console:
	uv run textual console - SYSTEM -X EVENT

release:
	@test -n "$(VERSION)" || (echo "Usage: make release VERSION=0.1.0" && exit 1)
	git tag -a "v$(VERSION)" -m "Release v$(VERSION)"
	git push origin "v$(VERSION)"
