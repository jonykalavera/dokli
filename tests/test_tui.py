"""TUI smoke tests."""

import asyncio

from dokli.config import Config, ConnectionConfig
from dokli.tui.app import DokliApp
from dokli.tui.engine import build_form_model, parse_spec
from dokli.tui.forms import Form, SelectControl, SwitchControl, TextAreaControl
from dokli.tui.screens.generic.confirm import ConfirmScreen
from dokli.tui.screens.generic.form import ActionFormScreen
from dokli.tui.screens.generic.home import EntityItem, HomeScreen
from dokli.tui.screens.generic.record import ActionItem, RecordScreen
from dokli.tui.screens.generic.wizard import WizardScreen

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
                                "properties": {
                                    "name": {"type": "string"},
                                    "description": {"type": "string"},
                                },
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


def test_form_prefills_from_data():
    """We expect Form.from_model to prefill controls from the data kwarg."""
    model = build_form_model({"properties": {"name": {"type": "string"}}})
    form = Form.from_model(model, data={"name": "prefilled"})
    assert form.fields["name"].value == "prefilled"


def test_form_rich_controls():
    """We expect enums, booleans and objects to map to rich controls."""
    model = build_form_model(
        {
            "properties": {
                "mode": {"type": "string", "enum": ["dev", "prod"]},
                "enabled": {"type": "boolean"},
                "labels": {"type": "object"},
                "name": {"type": "string"},
            }
        }
    )
    form = Form.from_model(model, data={"enabled": True, "labels": {"a": 1}})
    assert isinstance(form.fields["mode"], SelectControl)
    assert isinstance(form.fields["enabled"], SwitchControl)
    assert isinstance(form.fields["labels"], TextAreaControl)
    assert form.fields["enabled"].get_data() is True


def test_wizard_steps_through_fields(mocker):
    """We expect the wizard to step through fields one at a time."""
    connection = ConnectionConfig(name="test-env", url="https://example.com", api_key_cmd="echo key")
    config = Config(connections=[connection])
    mocker.patch("dokli.tui.app.APIClient")
    registry = parse_spec(FAKE_SCHEMA)
    action = registry.get("project").get("create")

    async def main():
        app = DokliApp(config=config)
        async with app.run_test() as pilot:
            screen = WizardScreen(connection, action)
            app.install_screen(screen, name="wizard")
            app.push_screen("wizard")
            await pilot.pause()
            prompt = app.screen.query_one("#prompt")
            assert "1/2" in str(prompt.renderable)
            await pilot.press("ctrl+n")
            await pilot.pause()
            assert "2/2" in str(app.screen.query_one("#prompt").renderable)

    _run(main())


def test_form_control_coerces_non_string_values():
    """We expect boolean fields to map to a switch and not crash the input."""
    model = build_form_model({"properties": {"autoDeploy": {"type": "boolean"}}})
    form = Form.from_model(model, data={"autoDeploy": True})
    from dokli.tui.forms import SwitchControl

    assert isinstance(form.fields["autoDeploy"], SwitchControl)
    assert form.fields["autoDeploy"].get_data() is True


def test_form_submit_asks_confirmation(mocker):
    """We expect submitting a form to require explicit confirmation first."""
    connection = ConnectionConfig(name="test-env", url="https://example.com", api_key_cmd="echo key")
    config = Config(connections=[connection])
    mocker.patch("dokli.tui.app.APIClient")
    mocker.patch("dokli.tui.screens.generic.execute.APIClient")
    registry = parse_spec(FAKE_SCHEMA)
    action = registry.get("project").get("create")

    async def main():
        app = DokliApp(config=config)
        async with app.run_test() as pilot:
            screen = ActionFormScreen(connection, action)
            app.install_screen(screen, name="form")
            app.push_screen("form")
            await pilot.pause()
            screen.form.fields["name"].value = "test"
            await pilot.press("ctrl+s")
            await pilot.pause()
            assert isinstance(app.screen, ConfirmScreen)

    _run(main())


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


def test_record_screen_resume_does_not_duplicate(mocker):
    """We expect resuming a record screen (e.g. after closing a form) not to duplicate actions."""
    connection = ConnectionConfig(name="test-env", url="https://example.com", api_key_cmd="echo key")
    config = Config(connections=[connection])
    mocker.patch("dokli.tui.app.APIClient")
    registry = parse_spec(FAKE_SCHEMA)
    record = {"projectId": "p1", "name": "app"}

    response = mocker.Mock()
    response.json.return_value = record
    client = mocker.Mock()
    client.request.return_value = response
    mocker.patch("dokli.tui.screens.generic.record.APIClient", return_value=client)

    async def main():
        app = DokliApp(config=config)
        async with app.run_test() as pilot:
            screen = RecordScreen(connection, registry, "project", record)
            app.install_screen(screen, name="record")
            app.push_screen("record")
            await pilot.pause()
            screen.on_screen_resume(None)
            await pilot.pause()
            screen.on_screen_resume(None)
            await pilot.pause()
            actions = [
                child
                for child in screen.query_one("#actions").children
                if isinstance(child, ActionItem)
            ]
            verbs = [action.verb for action in actions]
            assert verbs == ["create"]

    _run(main())
