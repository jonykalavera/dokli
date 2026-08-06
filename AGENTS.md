# AGENTS.md

Python CLI/TUI for [Dokploy](https://github.com/Dokploy/dokploy), generated from the OpenAPI document (auto-generating philosophy: CLI commands, TUI screens, and — planned — the as-code manifest).

## Commands

Use `uv` (migrated from poetry); Python 3.11 in `.venv` (`.python-version`).

- `make lint` — `ruff check dokli/` then `mypy dokli`. Run both; CI runs `make lint test`.
- `make test` — `uv run pytest -vv --cov dokli --blockage`.
- Single test: `uv run pytest tests/test_tui.py::test_name -q`.
- `make format` — `ruff format` + `ruff check --fix`.
- `make dev-tui` — run the TUI in dev mode (`dokli.tui.app:DokliApp`). Needs a Nerd Font for the icons.

## Git workflow

- `commit-msg` hook prefixes every message with `<branch>: `.
- Branch convention: `DOKLI-<issue>-f<phase>` (e.g. `DOKLI-42-f3`). One PR per phase; the user merges them.
- Release: bump `version` in `pyproject.toml`, commit, then `make release VERSION=X.Y.Z` (tags + pushes). CI `release.yml` fails if the pyproject version ≠ tag, then publishes to PyPI via trusted publishing (OIDC). Do not tag a release without bumping the version.

## Testing gotchas

- **`make test` needs the live config reachable.** `test_cli.py` collection imports `dokli.cli`, which calls `register_connections` and fetches the OpenAPI schema for every connection in `~/.config/dokli/dokli.yaml` at import time. An unreachable/polluted config breaks collection with a 404. Restore the real config (`connections: [meche]`) if tests overwrite it.
- **Never let tests write the real config.** App persistence handlers call `Config.save()`; tests must `mocker.patch("dokli.config.Config.save")` (pydantic blocks `patch.object` on an instance — patch the class). A stray real save overwrites the user's `~/.config/dokli/dokli.yaml`.
- TUI tests live in `tests/test_tui.py`: reuse `FAKE_SCHEMA`, `_patch_api(mocker)` (returns the responses dict + patches both APIClient sites), `FakeResponse`, and the pilot helpers `_mount_browser` / `_wait_for_label` / `_select`. Call `clear_probe_cache("test-env")` when changing probe responses.

## TUI specifics

- **Engine** (`dokli/tui/engine/`): `spec.py` builds the entity registry from `settings.getOpenApiDocument` and assigns deterministic keybindings; `probe.py` hides entities whose `all` returns 401/403 or needs params; `related.py` finds containers via `compose.one.appName` (the docker project slug) + `appType`, enriching list records through the entity's `one` action — do not match containers by the display `name`.
- **Keybindings**: `D` = dark mode, `F5` = refresh, `L` = readLogs. `RESERVED_KEYS = "hjklrq"` and `SYSTEM_KEYS = frozenset("D")` in `spec.py` — never assign those to actions (`l` is drill-in).
- **Pilot testing quirks** (hard-won):
  - `push_screen(screen, cb)` callbacks never fire under the pilot; await the result with `push_screen_wait` from a worker instead.
  - `run_worker(..., exclusive=True)` cancels other workers in the same group — e.g. the resume re-render cancels action workers. Put action workers in a distinct group (`group="action"`).
  - An `Input` composed in a screen gets auto-focused on mount, so a `/` search binding types into it instead of firing — set `can_focus=False` initially and enable it when opened.
  - Rich markup: close combined open tags like `[b green]` with `[/]`, not `[/b]`.

## Live instance

`meche` = https://dokploy.meche.lan (api key via `secret-tool lookup dokli meche`), configured in `~/.config/dokli/dokli.yaml`. The OpenAPI schema is cached per connection at `~/.config/dokli/cache/<conn>.openapi.json`; `dokli refresh [connection]` refetches it. Use this instance for manual CLI/TUI verification.

## Layout

- `dokli/cli.py` — typer entrypoint (`dokli = "dokli.cli:app"`); the `api` group is built from the schema at import (network).
- `dokli/manifest.py` / `apply.py` / `export.py` / `state.py` / `diff.py` — "Dokli as Code" (typed projects/services; plan/apply is additive, never deletes).
- `dokli/tui/app.py` — app, Catppuccin design, command palette provider.
- `dokli/tui/screens/generic/` — `browser.py` (3-column), `picker.py`, `result.py` (search `/` + `F5`), `help.py`, `form.py` / `wizard.py` / `confirm.py`; `dokli/tui/screens/connections.py` / `connection.py`.
