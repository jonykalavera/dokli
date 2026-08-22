# AGENTS.md

Python CLI/TUI for [Dokploy](https://github.com/Dokploy/dokploy), generated from the OpenAPI document (auto-generating philosophy: CLI commands, TUI screens, and — planned — the as-code manifest).

## Language

All collaboration content must be in **English** to ease contributions from anyone: commit messages, PR descriptions, issues/tickets, code comments and docstrings, README/docs, and config samples. No Spanish (or other languages) in code or GitHub content.

## Environment data

Never leak **environment-specific data** in collaboration content (PR descriptions, issues, comments, commit messages, README, examples, AGENTS.md): connection names, instance hostnames/URLs, api-key keyring labels, real service/project/environment names, real ids, or instance-specific counts. Smoke-test notes must be anonymized (e.g. "a real connection", "a github-sourced compose", "a deployment log") or use placeholders like `<conn>`, `<id>`, `<compose>`. This applies to every file in the repo, including this one.

## Commands

Use `uv` (migrated from poetry); Python 3.11 in `.venv` (`.python-version`).

- `make lint` — `ruff check dokli/` then `ty check dokli` (Astral's type checker; strict by default, native pydantic support). Run both; CI runs `make lint test`.
- `make test` — `uv run pytest -vv --cov dokli --blockage`.
- Single test: `uv run pytest tests/test_tui.py::test_name -q`.
- `make format` — `ruff format` + `ruff check --fix`.
- `make dev-tui` — run the TUI in dev mode (`dokli.tui.app:DokliApp`). Needs a Nerd Font for the icons.
- `make screenshots` — regenerate the README images (`tools/screenshots.py`, anonymous mock data only). Rasterizes Textual's compositor cell grid with the Agave Nerd Font Mono (Pillow), outputting PNGs to `assets/`.

## Git workflow

- `commit-msg` hook prefixes every message with `<branch>: `.
- Branch convention: `DOKLI-<issue>-f<phase>` (e.g. `DOKLI-42-f3`). One PR per phase; the user merges them.
- Release: bump `version` in `pyproject.toml`, commit, then `make release VERSION=X.Y.Z` (tags + pushes). CI `release.yml` fails if the pyproject version ≠ tag, then publishes to PyPI via trusted publishing (OIDC). Do not tag a release without bumping the version.

## Testing gotchas

- **`make test` needs the live config reachable.** `test_cli.py` collection imports `dokli.cli`, which calls `register_connections` and fetches the OpenAPI schema for every connection in `~/.config/dokli/dokli.yaml` at import time. An unreachable/polluted config breaks collection with a 404. Restore the real config (`connections: [<conn>]`) if tests overwrite it.
- **Never let tests write the real config.** App persistence handlers call `Config.save()`; tests must `mocker.patch("dokli.config.Config.save")` (pydantic blocks `patch.object` on an instance — patch the class). A stray real save overwrites the user's `~/.config/dokli/dokli.yaml`.
- TUI tests live in `tests/test_tui.py`: reuse `FAKE_SCHEMA`, `_patch_api(mocker)` (returns the responses dict + patches both APIClient sites), `FakeResponse`, and the pilot helpers `_mount_browser` / `_wait_for_label` / `_select`.

## TUI specifics

- **Engine** (`dokli/tui/engine/`): `spec.py` builds the entity registry from `settings.getOpenApiDocument` and assigns deterministic keybindings; `related.py` finds containers via `compose.one.appName` (the docker project slug) + `appType`, enriching list records through the entity's `one` action — do not match containers by the display `name`.
- **Keybindings**: `D` = dark mode, `F5` = refresh, `L` = readLogs, `ctrl+p` = command palette, `f4` = action picker (palette pre-filtered to the record's actions). Only **curated** verbs get a direct key (`VERB_KEYS` in `spec.py`: create `c`, update `u`, start `s`, stop `o`, deploy `x`, readLogs `L`, ...); everything else is reached via the palette/picker. `RESERVED_KEYS = "hjklrqy"` and `SYSTEM_KEYS = frozenset("D")` in `spec.py` — never assign those to actions (`l` is drill-in, `y` yanks the id).
- **Pilot testing quirks** (hard-won):
  - `push_screen(screen, cb)` callbacks never fire under the pilot; await the result with `push_screen_wait` from a worker instead.
  - `run_worker(..., exclusive=True)` cancels other workers in the same group — e.g. the resume re-render cancels action workers. Put action workers in a distinct group (`group="action"`).
  - An `Input` composed in a screen gets auto-focused on mount, so a `/` search binding types into it instead of firing — set `can_focus=False` initially and enable it when opened.
  - Rich markup: close combined open tags like `[b green]` with `[/]`, not `[/b]`.

## Live instance

One local connection (a self-hosted Dokploy on the LAN, api key in the system keyring) is configured in `~/.config/dokli/dokli.yaml`. The OpenAPI schema is cached per connection at `~/.config/dokli/cache/<conn>.openapi.json`; `dokli refresh [connection]` refetches it. Use a real connection for manual CLI/TUI verification.

## Layout

- `dokli/cli.py` — typer entrypoint (`dokli = "dokli.cli:app"`); the `api` group is built from the schema at import (network).
- `dokli/manifest.py` / `apply.py` / `export.py` / `state.py` / `diff.py` — "Dokli as Code" (typed projects/services; plan/apply is additive, never deletes).
- `dokli/tui/app.py` — app, Catppuccin design, command palette provider.
- `dokli/tui/screens/generic/` — `browser.py` (3-column), `picker.py`, `result.py` (search `/` + `F5`), `help.py`, `form.py` / `wizard.py` / `confirm.py`; `dokli/tui/screens/connections.py` / `connection.py`.
