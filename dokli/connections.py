"""CLI commands to manage connections (issue #47)."""

import typer
import yaml
from pydantic import ValidationError
from rich import print as rprint
from rich.table import Table

from dokli.api_client import APIClient
from dokli.config import Config, ConnectionConfig, complete_connection_names
from dokli.formatting import redact_secrets
from dokli.secrets import conn_account, set_secret


def build_command(config: Config) -> typer.Typer:
    """Build the ``dokli connections`` command group bound to ``config``."""
    group = typer.Typer(name="connections", help="Manage connections.", no_args_is_help=True)

    @group.command("ls")
    def list_connections() -> None:
        """List connections."""
        _list_connections(config)

    @group.command("add")
    def add_connection(
        name: str | None = typer.Argument(None, help="Connection name (lowercase, hyphen-separated)."),
        url: str | None = typer.Option(None, "--url", help="Dokploy instance URL."),
        api_key: str | None = typer.Option(None, "--api-key", help="API key (64 chars)."),
        api_key_cmd: str | None = typer.Option(None, "--api-key-cmd", help="Command that outputs the API key."),
        keyring: bool = typer.Option(
            False, "--keyring", help="Store the API key in the system keychain instead of the config file."
        ),
        notes: str | None = typer.Option(None, "--notes", help="Notes about the connection."),
    ) -> None:
        """Add a connection (missing values are prompted)."""
        _add_connection(config, name, url, api_key, api_key_cmd, keyring, notes)

    @group.command("update")
    def update_connection(
        name: str = typer.Argument(..., help="Connection name.", shell_complete=complete_connection_names),
        new_name: str | None = typer.Argument(None, help="New name (renames the connection)."),
        url: str | None = typer.Option(None, "--url", help="New URL."),
        api_key: str | None = typer.Option(None, "--api-key", help="New API key (64 chars)."),
        api_key_cmd: str | None = typer.Option(None, "--api-key-cmd", help="New command that outputs the API key."),
        keyring: bool = typer.Option(False, "--keyring", help="Move the API key to the system keychain."),
        notes: str | None = typer.Option(None, "--notes", help="New notes."),
    ) -> None:
        """Update a connection (optionally renaming it)."""
        _update_connection(config, name, new_name, url, api_key, api_key_cmd, keyring, notes)

    @group.command("remove")
    def remove_connection(
        name: str = typer.Argument(..., help="Connection name.", shell_complete=complete_connection_names),
    ) -> None:
        """Remove a connection."""
        _remove_connection(config, name)

    @group.command("get")
    def get_connection(
        name: str = typer.Argument(..., help="Connection name.", shell_complete=complete_connection_names),
    ) -> None:
        """Show a connection (key masked)."""
        _get_connection(config, name)

    @group.command("test")
    def test_connection(
        name: str = typer.Argument(..., help="Connection name.", shell_complete=complete_connection_names),
    ) -> None:
        """Validate a connection against the live instance."""
        _test_connection(config, name)

    return group


def set_default_connection(config: Config, name: str) -> None:
    """Set the default connection (used when none is passed) and persist it."""
    _find(config, name)
    config.default_connection = name
    config.save()
    rprint(f"[green]Default connection set to '{name}'.[/green]")


def unset_default_connection(config: Config) -> None:
    """Clear the default connection and persist."""
    config.default_connection = None
    config.save()
    rprint("[green]Default connection cleared.[/green]")


def _find(config: Config, name: str) -> ConnectionConfig:
    for connection in config.connections:
        if connection.name == name:
            return connection
    raise typer.BadParameter(f"Unknown connection '{name}'.")


def _mask(connection: ConnectionConfig) -> str:
    if connection.api_key is not None:
        key = connection.api_key.get_secret_value()
        return f"{key[:4]}…{key[-4:]}"
    if connection.api_key_cmd:
        return f"cmd: {connection.api_key_cmd}"
    return ""


def _list_connections(config: Config) -> None:
    table = Table(title="Connections")
    table.add_column("Name")
    table.add_column("URL")
    table.add_column("Key")
    table.add_column("Notes")
    for connection in config.connections:
        table.add_row(connection.name, str(connection.url), _mask(connection), connection.notes)
    rprint(table)


def _add_connection(
    config: Config,
    name: str | None,
    url: str | None,
    api_key: str | None,
    api_key_cmd: str | None,
    keyring: bool,
    notes: str | None,
) -> None:
    if not name:
        name = typer.prompt("Connection name")
    if any(connection.name == name for connection in config.connections):
        raise typer.BadParameter(f"Connection '{name}' already exists.")
    if not url:
        url = typer.prompt("URL")
    if keyring:
        if not api_key:
            api_key = typer.prompt("API key", hide_input=True)
        set_secret(conn_account(name), api_key)
        data = {
            "name": name,
            "url": url,
            "api_key": None,
            "api_key_cmd": None,
            "api_key_keyring": True,
            "notes": notes or "",
        }
    else:
        if not api_key and not api_key_cmd:
            api_key = typer.prompt("API key", hide_input=True)
        data = {"name": name, "url": url, "api_key": api_key, "api_key_cmd": api_key_cmd, "notes": notes or ""}
    try:
        connection = ConnectionConfig.model_validate(data)
    except ValidationError as err:
        raise typer.BadParameter(err.errors()[0]["msg"]) from None
    config.connections = [*config.connections, connection]
    config.save()
    rprint(f"[green]Added connection '{name}'.[/green]")


def _update_connection(
    config: Config,
    name: str,
    new_name: str | None,
    url: str | None,
    api_key: str | None,
    api_key_cmd: str | None,
    keyring: bool,
    notes: str | None,
) -> None:
    current = _find(config, name)
    renaming = new_name is not None and new_name != name
    has_fields = url is not None or api_key is not None or api_key_cmd is not None or keyring or notes is not None
    if new_name is not None and not renaming and has_fields:
        rprint(f"[yellow]'{name}' is already named '{new_name}' (rename skipped).[/yellow]")
    if not renaming and not has_fields:
        rprint(f"[yellow]No fields provided to update for '{name}'.[/yellow]")
        return
    if renaming and any(connection.name == new_name for connection in config.connections):
        raise typer.BadParameter(f"Connection '{new_name}' already exists.")
    data = current.model_dump_clear()
    if renaming:
        data["name"] = new_name
    if url is not None:
        data["url"] = url
    if keyring:
        set_secret(conn_account(name), current.get_api_key())
        data["api_key"] = None
        data["api_key_cmd"] = None
        data["api_key_keyring"] = True
    elif api_key is not None:
        data["api_key"] = api_key
        data["api_key_cmd"] = None
        data["api_key_keyring"] = False
    elif api_key_cmd is not None:
        data["api_key_cmd"] = api_key_cmd
        data["api_key"] = None
        data["api_key_keyring"] = False
    if notes is not None:
        data["notes"] = notes
    try:
        updated = ConnectionConfig(**data)
    except ValidationError as err:
        raise typer.BadParameter(err.errors()[0]["msg"]) from None
    config.connections = [updated if c.name == name else c for c in config.connections]
    config.save()
    label = f"'{name}' → '{new_name}'" if renaming else f"'{name}'"
    rprint(f"[green]Updated connection {label}.[/green]")


def _remove_connection(config: Config, name: str) -> None:
    _find(config, name)
    config.connections = [connection for connection in config.connections if connection.name != name]
    config.save()
    rprint(f"[green]Removed connection '{name}'.[/green]")


def _get_connection(config: Config, name: str) -> None:
    connection = _find(config, name)
    data = redact_secrets(connection.model_dump_clear())
    rprint(yaml.dump(data, sort_keys=False))


def _test_connection(config: Config, name: str) -> None:
    connection = _find(config, name)
    try:
        schema = APIClient(connection, force_refresh=True).schema
    except Exception as err:
        rprint(f"[red]Connection '{name}' is unreachable: {err}[/red]")
        raise typer.Exit(code=1) from None
    version = (schema.get("info") or {}).get("version", "unknown")
    rprint(f"[green]Connection '{name}' OK — Dokploy API {version}.[/green]")
