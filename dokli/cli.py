"""Dokli CLI."""

import asyncio
import json
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as package_version
from typing import Any

import typer
import yaml
from rich import print as rprint
from rich.table import Table

from dokli.api_client import APIClient
from dokli.apply import Applier
from dokli.config import Config, ConnectionConfig, complete_connection_names
from dokli.connections import build_command as build_connections_command
from dokli.diff import build_plan
from dokli.export import export_manifest
from dokli.formatting import Format, redact_secrets
from dokli.init import init_manifest
from dokli.manifest import load_manifests
from dokli.openapi_cli import build_command as build_api_command
from dokli.report import ApplyReport
from dokli.secrets_cli import build_command as build_secrets_command
from dokli.state import collect_state
from dokli.validate import validate_manifest
from dokli.wss import LOGS_ENDPOINT, iter_lines

try:
    from dokli.tui.app import app as tui

    _tui_loaded = True
except ImportError:
    _tui_loaded = False

app = typer.Typer()
state: dict[str, Any] = {
    "config": Config(),
}
app.add_typer(build_api_command(state["config"]))
app.add_typer(build_connections_command(state["config"]))
app.add_typer(build_secrets_command())


def tui_command(
    connection_name: str | None = typer.Argument(
        None, help="Connection name.", shell_complete=complete_connection_names
    ),
) -> None:
    """Text User Interface."""
    assert tui, "TUI not loaded"
    tui.config = state["config"]
    if connection_name is not None:
        tui.connection = _get_connection(connection_name)
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


@app.command(name="init")
def init_command(
    output: str = typer.Option("dokploy.yaml", "--output", "-o", help="Output file."),
) -> None:
    """Scaffold a new dokli manifest."""
    try:
        path = init_manifest(state["config"], output)
    except FileExistsError as err:
        rprint(f"[red]{err}[/red]")
        raise typer.Exit(code=1) from None
    rprint(f"[green]Wrote {path}[/green]")


@app.command(name="refresh")
def refresh_command(
    connection_name: str | None = typer.Argument(
        None, help="Connection name.", shell_complete=complete_connection_names
    ),
) -> None:
    """Refetch and refresh the cached OpenAPI schema for a connection."""
    connection = _get_connection(connection_name)
    APIClient(connection, force_refresh=True)
    rprint(f"[green]Refreshed OpenAPI schema for {connection.name}.[/green]")


@app.command(name="schema")
def schema_command(
    connection_name: str | None = typer.Argument(
        None, help="Connection name.", shell_complete=complete_connection_names
    ),
    format: Format = Format.json,
    refresh: bool = typer.Option(False, "--refresh", help="Refetch the schema instead of using the cache."),
    summary: bool = typer.Option(False, "--summary", help="Print a compact overview instead of the full schema."),
) -> None:
    """Show the OpenAPI schema of a connection."""
    connection = _get_connection(connection_name)
    schema = APIClient(connection, force_refresh=refresh).schema
    if summary:
        _print_schema_summary(connection, schema)
    elif format == Format.yaml:
        rprint(yaml.safe_dump(schema, sort_keys=False))
    else:
        rprint(json.dumps(schema, indent=2))


def _print_schema_summary(connection: ConnectionConfig, schema: dict) -> None:
    """Print a compact overview of a connection's OpenAPI schema."""
    info = schema.get("info", {}) or {}
    paths = schema.get("paths", {}) or {}
    schemas = (schema.get("components", {}) or {}).get("schemas", {}) or {}
    rprint(f"Connection: {connection.name}")
    rprint(f"URL: {connection.url}")
    rprint(f"Title: {info.get('title', '-')}")
    rprint(f"Dokploy API version: {info.get('version', '-')}")
    rprint(f"Paths: {len(paths)}")
    rprint(f"Schemas: {len(schemas)}")


@app.command(name="logs")
def logs_command(
    connection_name: str | None = typer.Argument(
        None, help="Connection name.", shell_complete=complete_connection_names
    ),
    container_id: str = typer.Option(None, "--container-id", help="Docker container id."),
    tail: int = typer.Option(500, "--tail", help="Lines of history to show first."),
) -> None:
    """Stream a container's live logs over WebSocket (Ctrl+C to stop)."""
    connection = _get_connection(connection_name)
    if not container_id:
        raise typer.BadParameter("--container-id is required.")
    asyncio.run(_stream_container_logs(connection, container_id, tail))


async def _stream_container_logs(connection: ConnectionConfig, container_id: str, tail: int) -> None:
    """Print a container's live logs as they arrive over the WebSocket."""
    try:
        async for line in iter_lines(connection, LOGS_ENDPOINT, {"containerId": container_id, "tail": tail}):
            print(line.rstrip("\r"))  # noqa: T201
    except KeyboardInterrupt:
        pass


@app.command(name="state")
def state_command(
    connection_name: str | None = typer.Argument(
        None, help="Connection name.", shell_complete=complete_connection_names
    ),
    show_secrets: bool = typer.Option(False, "--show-secrets", help="Show environment variables (secrets)."),
) -> None:
    """Show the current state of a Dokploy instance."""
    connection = _get_connection(connection_name)
    live_state = collect_state(connection)
    data = live_state.model_dump(mode="json")
    if not show_secrets:
        data = redact_secrets(data)
    rprint(yaml.dump(data))


@app.command(name="plan")
def plan_command(
    manifest_file: str = typer.Option("dokploy.yaml", "--file", "-f", help="Path to a manifest file or directory."),
    prune: bool = typer.Option(
        False, "--prune", help="Also plan deletions of resources/services not in the manifest."
    ),
) -> None:
    """Show what would change between the manifest(s) and the live instances."""
    manifests = load_manifests(manifest_file)
    if not manifests:
        raise typer.BadParameter(f"No manifests found in '{manifest_file}'.")
    if prune:
        for manifest in manifests:
            connection = _get_connection(manifest.connection)
            if len(manifests) > 1:
                rprint(f"[bold]{manifest.connection}[/bold]")
            report = Applier(manifest, connection).run(dry_run=True, prune=True)
            _print_apply_report(report)
        return
    changed = False
    for manifest in manifests:
        connection = _get_connection(manifest.connection)
        live_state = collect_state(connection)
        plan = build_plan(manifest, live_state)
        if not plan.has_changes:
            continue
        changed = True
        if len(manifests) > 1:
            rprint(f"[bold]{manifest.connection}[/bold]")
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
    if not changed:
        rprint("[green]No changes.[/green]")


def _print_apply_report(report: ApplyReport) -> None:
    if not report.actions:
        rprint("[green]No changes.[/green]")
    else:
        table = Table(title="Apply report")
        table.add_column("Action")
        table.add_column("Kind")
        table.add_column("Project")
        table.add_column("Name")
        table.add_column("Details")
        for action in report.actions:
            table.add_row(action.action, action.kind, action.project, action.name, action.details)
        rprint(table)
    for warning in report.warnings:
        rprint(f"[yellow]{warning}[/yellow]")


@app.command(name="apply")
def apply_command(
    manifest_file: str = typer.Option("dokploy.yaml", "--file", "-f", help="Path to a manifest file or directory."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would change without applying."),
    deploy: bool = typer.Option(False, "--deploy", help="Deploy services after applying."),
    prune: bool = typer.Option(
        False,
        "--prune",
        help="Delete resources/services not in the manifest (within declared projects).",
    ),
) -> None:
    """Apply a manifest (or every manifest in a directory) to Dokploy instances."""
    manifests = load_manifests(manifest_file)
    if not manifests:
        raise typer.BadParameter(f"No manifests found in '{manifest_file}'.")
    for manifest in manifests:
        connection = _get_connection(manifest.connection)
        applier = Applier(manifest, connection, deploy=deploy)
        report = applier.run(dry_run=dry_run, prune=prune)
        if len(manifests) > 1:
            rprint(f"[bold]{manifest_file} ({manifest.connection})[/bold]")
        _print_apply_report(report)


@app.command(name="validate")
def validate_command(
    manifest_file: str = typer.Option("dokploy.yaml", "--file", "-f", help="Path to a manifest file or directory."),
) -> None:
    """Validate a manifest (or every manifest in a directory) offline."""
    manifests = load_manifests(manifest_file)
    if not manifests:
        raise typer.BadParameter(f"No manifests found in '{manifest_file}'.")
    all_issues: list[str] = []
    for manifest in manifests:
        connection = _get_connection(manifest.connection)
        issues = validate_manifest(connection, manifest)
        if issues:
            all_issues.extend(f"[{manifest.connection}] {issue}" for issue in issues)
    if all_issues:
        for issue in all_issues:
            rprint(f"[yellow]{issue}[/yellow]")
        raise typer.Exit(code=1)
    rprint("[green]Manifests are valid.[/green]")


@app.command(name="export")
def export_command(
    connection_name: str | None = typer.Argument(
        None, help="Connection name.", shell_complete=complete_connection_names
    ),
    output: str = typer.Option("dokploy.yaml", "--output", "-o", help="Output file, or '-' for stdout."),
    include_secrets: bool = typer.Option(False, "--include-secrets", help="Export environment variables (secrets)."),
) -> None:
    """Export the live state of an instance into a manifest."""
    connection = _get_connection(connection_name)
    manifest, warnings = export_manifest(connection, include_secrets=include_secrets)
    content = yaml.safe_dump(manifest.model_dump(mode="json", exclude_none=True, by_alias=True), sort_keys=False)
    if output == "-":
        rprint(content)
    else:
        with open(output, "w") as file:
            file.write(content)
        rprint(f"[green]Wrote {output}[/green]")
    for warning in warnings:
        rprint(f"[yellow]{warning}[/yellow]")


@app.callback(no_args_is_help=True, invoke_without_command=True)
def main(
    version: bool = typer.Option(False, "--version", "-v", is_eager=True, help="Show the version and exit."),
) -> None:
    """Magical Dokploy CLI/TUI."""
    if version:
        rprint(f"dokli {_cli_version()}")
        raise typer.Exit()


def _cli_version() -> str:
    """The installed package version (single source: ``pyproject.toml``)."""
    try:
        return package_version("dokli")
    except PackageNotFoundError:
        return "unknown"
