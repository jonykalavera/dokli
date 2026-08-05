"""Dokli CLI."""

from typing import Any

import typer
import yaml
from rich import print as rprint
from rich.table import Table

from dokli.apply import Applier
from dokli.config import Config, ConnectionConfig
from dokli.diff import build_plan
from dokli.export import export_manifest
from dokli.manifest import Manifest
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


@app.command(name="plan")
def plan_command(
    manifest_file: str = typer.Option("dokploy.yaml", "--file", "-f", help="Path to the manifest."),
) -> None:
    """Show what would change between the manifest and the live instance."""
    manifest = Manifest.load(manifest_file)
    connection = _get_connection(manifest.connection)
    live_state = collect_state(connection)
    plan = build_plan(manifest, live_state)
    if not plan.has_changes:
        rprint("[green]No changes.[/green]")
        return
    table = Table(title=f"Plan for {manifest.connection}")
    table.add_column("Action")
    table.add_column("Kind")
    table.add_column("Project")
    table.add_column("Name")
    table.add_column("Details")
    for item in plan.items:
        details = ", ".join(item.changed) if item.changed else item.reason
        table.add_row(item.action, item.kind, item.project, item.name, details)
    rprint(table)


def _print_apply_report(report) -> None:
    if not report.actions:
        rprint("[green]No changes.[/green]")
        return
    table = Table(title="Apply report")
    table.add_column("Action")
    table.add_column("Kind")
    table.add_column("Project")
    table.add_column("Name")
    table.add_column("Details")
    for action in report.actions:
        table.add_row(action.action, action.kind, action.project, action.name, action.details)
    rprint(table)


@app.command(name="apply")
def apply_command(
    manifest_file: str = typer.Option("dokploy.yaml", "--file", "-f", help="Path to the manifest."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would change without applying."),
    deploy: bool = typer.Option(False, "--deploy", help="Deploy services after applying."),
) -> None:
    """Apply the manifest to a Dokploy instance (idempotent, additive)."""
    manifest = Manifest.load(manifest_file)
    connection = _get_connection(manifest.connection)
    applier = Applier(manifest, connection, deploy=deploy)
    report = applier.run(dry_run=dry_run)
    _print_apply_report(report)


@app.command(name="export")
def export_command(
    connection_name: str | None = typer.Argument(None, help="Connection name."),
    output: str = typer.Option("dokploy.yaml", "--output", "-o", help="Output file, or '-' for stdout."),
    include_secrets: bool = typer.Option(False, "--include-secrets", help="Export environment variables (secrets)."),
) -> None:
    """Export the live state of an instance into a manifest."""
    connection = _get_connection(connection_name)
    manifest, warnings = export_manifest(connection, include_secrets=include_secrets)
    content = yaml.safe_dump(manifest.model_dump(mode="json", exclude_none=True), sort_keys=False)
    if output == "-":
        rprint(content)
    else:
        with open(output, "w") as file:
            file.write(content)
        rprint(f"[green]Wrote {output}[/green]")
    for warning in warnings:
        rprint(f"[yellow]{warning}[/yellow]")


@app.callback(no_args_is_help=True)
def main() -> None:
    """Magical Dokploy CLI/TUI."""
