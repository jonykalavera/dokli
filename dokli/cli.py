"""Dokli CLI."""

from typing import Any

import typer
import yaml
from rich import print as rprint

from dokli.config import Config, ConnectionConfig
from dokli.openapi_cli import register_connections
from dokli.state import collect_state

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


def _get_connection(connection_name: str | None) -> ConnectionConfig:
    """Resolve a connection by name, or the only configured one."""
    config = state["config"]
    if connection_name is not None:
        for connection in config.connections:
            if connection.name == connection_name:
                return connection
        raise typer.BadParameter(f"Unknown connection '{connection_name}'.")
    if len(config.connections) == 1:
        return config.connections[0]
    raise typer.BadParameter("Specify a connection name.")


@app.command(name="state")
def state_command(connection_name: str | None = typer.Argument(None, help="Connection name.")) -> None:
    """Show the current state of a Dokploy instance."""
    connection = _get_connection(connection_name)
    live_state = collect_state(connection)
    rprint(yaml.dump(live_state.model_dump(mode="json")))


@app.callback(no_args_is_help=True)
def main() -> None:
    """Magical Dokploy CLI/TUI."""
