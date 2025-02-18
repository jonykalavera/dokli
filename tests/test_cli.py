"""Dokli CLI tests."""

from dokli.cli import app, main


def test_loads_api_commands(mocker):
    """We expect the CLI to load API commands."""
    assert app.registered_groups[0].typer_instance.info.name == "api"


def test_loads_tui_command():
    """We expect the CLI to load TUI command."""
    assert "tui" in [cmd.name for cmd in app.registered_commands]


def test_app_has_main_callback():
    """We expect the CLI to have a main callback."""
    assert app.registered_callback.callback is main
    assert app.registered_callback.no_args_is_help
