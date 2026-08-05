"""TUI smoke tests."""

import asyncio

from dokli.config import Config, ConnectionConfig
from dokli.tui.app import DokliApp
from dokli.tui.screens.generic.home import EntityItem, HomeScreen

FAKE_SCHEMA = {
    "paths": {
        "/project.all": {"get": {}},
        "/project.one": {
            "get": {"parameters": [{"name": "projectId", "in": "query", "required": True}]}
        },
        "/project.create": {
            "post": {
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {"name": {"type": "string"}},
                                "required": ["name"],
                            }
                        }
                    }
                }
            }
        },
        "/redis.all": {"get": {}},
    }
}


def _run(coro):
    return asyncio.run(coro)


async def _select_connection(app, pilot):
    list_view = app.screen.query_one("#connections-list")
    list_view.index = 0
    list_view.focus()
    await pilot.pause()
    await pilot.press("enter")
    await pilot.pause()


def test_connection_selection_opens_home(mocker):
    """We expect selecting a connection to open the entity browser."""
    connection = ConnectionConfig(name="test-env", url="https://example.com", api_key_cmd="echo key")
    config = Config(connections=[connection])
    client = mocker.Mock()
    client.schema = FAKE_SCHEMA
    mocker.patch("dokli.tui.app.APIClient", return_value=client)

    async def main():
        app = DokliApp(config=config)
        async with app.run_test() as pilot:
            await pilot.pause()
            await _select_connection(app, pilot)
            assert isinstance(app.screen, HomeScreen)

    _run(main())


def test_home_lists_core_entities(mocker):
    """We expect the home screen to list project and redis as core entities."""
    connection = ConnectionConfig(name="test-env", url="https://example.com", api_key_cmd="echo key")
    config = Config(connections=[connection])
    client = mocker.Mock()
    client.schema = FAKE_SCHEMA
    mocker.patch("dokli.tui.app.APIClient", return_value=client)

    async def main():
        app = DokliApp(config=config)
        async with app.run_test() as pilot:
            await pilot.pause()
            await _select_connection(app, pilot)
            items = [
                child for child in app.screen.query_one("#entities").children if isinstance(child, EntityItem)
            ]
            labels = [item.query_one("#name").renderable for item in items]
            assert any("project" in label for label in labels)
            assert any("redis" in label for label in labels)

    _run(main())
