"""Dokli CLI tests."""

import pytest
import typer

import dokli.cli
from dokli.cli import app, main, refresh_command, tui_command
from dokli.config import Config, ConnectionConfig
from dokli.openapi_cli import build_command


def test_loads_api_commands():
    """We expect the CLI to load API commands."""
    assert app.registered_groups[0].typer_instance.info.name == "api"


def test_loads_tui_command():
    """We expect the CLI to load TUI command."""
    assert "tui" in [cmd.name for cmd in app.registered_commands]


def test_loads_refresh_command():
    """We expect the CLI to load the refresh command."""
    assert "refresh" in [cmd.name for cmd in app.registered_commands]


def test_app_has_main_callback():
    """We expect the CLI to have a main callback."""
    assert app.registered_callback.callback is main
    assert app.registered_callback.no_args_is_help


def test_refresh_command_forces_refresh(mocker):
    """We expect refresh to force the schema refresh."""
    connection = ConnectionConfig(name="test-env", url="https://example.com", api_key_cmd="echo key")
    mocker.patch("dokli.cli._get_connection", return_value=connection)
    client = mocker.patch("dokli.cli.APIClient")

    refresh_command("test-env")

    client.assert_called_once_with(connection, force_refresh=True)


def test_tui_command_opens_connection_by_name(mocker):
    """We expect tui <name> to set the connection and run without the picker."""
    connection = ConnectionConfig(name="test-env", url="https://example.com", api_key_cmd="echo key")
    dokli.cli.tui.connection = None
    mocker.patch("dokli.cli._get_connection", return_value=connection)
    run = mocker.patch("dokli.cli.tui.run")

    tui_command("test-env")

    assert dokli.cli.tui.connection is connection
    run.assert_called_once_with()


def test_tui_command_without_name_keeps_picker(mocker):
    """We expect tui (no arg) to keep the interactive picker: no lookup, no connection."""
    get_connection = mocker.patch("dokli.cli._get_connection")
    run = mocker.patch("dokli.cli.tui.run")
    dokli.cli.tui.connection = None

    tui_command(None)

    get_connection.assert_not_called()
    assert dokli.cli.tui.connection is None
    run.assert_called_once_with()


def test_tui_command_unknown_name_raises(mocker):
    """We expect tui <unknown> to fail with a bad-parameter error."""
    mocker.patch("dokli.cli._get_connection", side_effect=typer.BadParameter("Unknown connection 'nope'."))

    with pytest.raises(typer.BadParameter):
        tui_command("nope")


def test_build_command_skips_broken_connection(mocker):
    """We expect a connection with an unresolvable key not to break the CLI."""
    good = ConnectionConfig(name="good", url="https://a.example.com", api_key="*" * 64)
    bad = ConnectionConfig(name="bad", url="https://b.example.com", api_key_cmd="secret-tool lookup dokli nope")

    def fake_register(connection):
        if connection.name == "bad":
            raise RuntimeError("api_key_cmd failed")
        return typer.Typer(name=connection.name)

    mocker.patch("dokli.openapi_cli._register_api_methods", side_effect=fake_register)
    app = typer.Typer()
    api_group = build_command(Config(connections=[good, bad]))
    app.add_typer(api_group)

    api_group = app.registered_groups[0].typer_instance
    names = [group.name for group in api_group.registered_groups]
    assert "good" in names
    assert "bad" not in names
