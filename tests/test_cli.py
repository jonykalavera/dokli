"""Dokli CLI tests."""

import pytest

from dokli.cli import app, state


@pytest.mark.skip
def test_loads_api_commands(mocker):
    """We expect the CLI to load API commands."""
    register_connections = mocker.patch("dokli.cli.register_connections", return_value=None)

    register_connections.assert_called_once_with(app, state["config"])


def test_loads_tui_command():
    """We expect the CLI to load TUI command."""
    assert app.registered_commands[-1].name == "tui"


def test_app_has_main_callback():
    """We expect the CLI to have a main callback."""
    assert app.registered_callback.no_args_is_help
