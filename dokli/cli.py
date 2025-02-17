"""Dokli CLI."""

from typing import Any

import typer

from dokli.config import Config
from dokli.openapi_cli import register_connections

try:
    from dokli.tui import app as tui

    _tui_loaded = True
except ImportError:
    _tui_loaded = False

app = typer.Typer()
state: dict[str, Any] = {
    "config": Config(),
}
register_connections(app, state["config"])


def tui_command() -> None:
    """Text User Interface."""
    assert tui, "TUI not loaded"
    tui.config = state["config"]
    tui.run()


if _tui_loaded:
    app.command(name="tui")(tui_command)


@app.callback(no_args_is_help=True)
def main():
    """Magical Dokploy CLI/TUI."""
