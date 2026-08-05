"""Dokli CLI tests."""

from dokli.cli import app, main, refresh_command
from dokli.config import ConnectionConfig


def test_loads_api_commands(mocker):
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
