"""TUI tests (browser navigation, forms, wizard)."""

import asyncio

from textual.containers import VerticalScroll
from textual.widgets import Label

from dokli.config import Config, ConnectionConfig
from dokli.tui.app import DokliApp
from dokli.tui.engine import build_form_model, parse_spec, record_title
from dokli.tui.forms import Form, SelectControl, SwitchControl, TextAreaControl
from dokli.tui.screens.generic.browser import BrowserScreen
from dokli.tui.screens.generic.confirm import ConfirmScreen
from dokli.tui.screens.generic.form import ActionFormScreen
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
        "/project.remove": {"post": {}},
        "/environment.one": {
            "get": {"parameters": [{"name": "environmentId", "in": "query", "required": True}]}
        },
        "/server.all": {"get": {}},
    }
}


class FakeResponse:
    """Minimal response stand-in."""

    def __init__(self, data):
        self._data = data

    def json(self):
        return self._data


def _connection() -> ConnectionConfig:
    return ConnectionConfig(name="test-env", url="https://example.com", api_key_cmd="echo key")


def _config() -> Config:
    return Config(connections=[_connection()])


def _fake_requests():
    return {
        "project.all": [{"projectId": "p1", "name": "media"}, {"projectId": "p2", "name": "services"}],
        "project.one": {
            "projectId": "p1",
            "name": "media",
            "environments": [
                {"environmentId": "e1", "name": "production", "isDefault": True}
            ],
        },
        "environment.one": {
            "environmentId": "e1",
            "name": "production",
            "compose": [{"composeId": "c1", "name": "torrents"}],
        },
    }


def _patch_api(mocker):
    client = mocker.Mock()
    responses = _fake_requests()

    def fake_request(method, path, params):
        return FakeResponse(responses.get(path, []))

    client.request.side_effect = fake_request
    mocker.patch("dokli.tui.screens.generic.browser.APIClient", return_value=client)
    mocker.patch("dokli.tui.app.APIClient", return_value=mocker.Mock(schema=FAKE_SCHEMA))
    return client


def _run(coro):
    return asyncio.run(coro)


async def _mount_browser(app, pilot, connection, registry):
    """Push the browser screen and wait for it to render."""
    screen = BrowserScreen(connection, registry)
    app.install_screen(screen, name="browser")
    app.push_screen("browser")
    for _ in range(30):
        await pilot.pause()
        if _current_labels(app):
            return
    raise AssertionError("Browser did not render entities")


async def _wait_for_label(app, pilot, label):
    """Wait until the current list shows the given label."""
    for _ in range(30):
        await pilot.pause()
        if any(label in current for current in _current_labels(app)):
            return
    raise AssertionError(f"Label {label!r} never appeared")


def _current_labels(app):
    labels = [
        str(label.renderable)
        for label in app.screen.query_one("#current-pane", VerticalScroll).children
        if isinstance(label, Label)
    ]
    return labels


def _select(app, label):
    screen = app.screen
    index = next(
        i
        for i, item in enumerate(screen.current.items)
        if record_title(item) == label
    )
    screen.current.index = index


# -- forms ----------------------------------------------------------------


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


def test_multiline_string_fields():
    """We expect known multiline and newline-valued strings to be text areas."""
    model = build_form_model(
        {"properties": {"description": {"type": "string"}, "name": {"type": "string"}}}
    )
    form = Form.from_model(model, data={"description": "line1\nline2"})
    assert isinstance(form.fields["description"], TextAreaControl)
    assert form.fields["description"].get_data() == "line1\nline2"
    assert not isinstance(form.fields["name"], TextAreaControl)


def test_form_submit_asks_confirmation(mocker):
    """We expect submitting a form to require explicit confirmation first."""
    mocker.patch("dokli.tui.app.APIClient")
    mocker.patch("dokli.tui.screens.generic.execute.APIClient")
    registry = parse_spec(FAKE_SCHEMA)
    action = registry.get("project").get("create")

    async def main():
        app = DokliApp(config=_config())
        async with app.run_test() as pilot:
            screen = ActionFormScreen(_connection(), action)
            app.install_screen(screen, name="form")
            app.push_screen("form")
            await pilot.pause()
            screen.form.fields["name"].value = "test"
            await pilot.press("ctrl+s")
            await pilot.pause()
            assert isinstance(app.screen, ConfirmScreen)

    _run(main())


def test_wizard_steps_through_fields(mocker):
    """We expect the wizard to step through fields one at a time."""
    mocker.patch("dokli.tui.app.APIClient")
    registry = parse_spec(FAKE_SCHEMA)
    action = registry.get("project").get("create")

    async def main():
        app = DokliApp(config=_config())
        async with app.run_test() as pilot:
            screen = WizardScreen(_connection(), action)
            app.install_screen(screen, name="wizard")
            app.push_screen("wizard")
            await pilot.pause()
            assert "1/2" in str(app.screen.query_one("#prompt").renderable)
            await pilot.press("ctrl+n")
            await pilot.pause()
            assert "2/2" in str(app.screen.query_one("#prompt").renderable)

    _run(main())


# -- browser --------------------------------------------------------------


def test_browser_starts_at_entities(mocker):
    """We expect the browser to start with listable entities in the middle column."""
    _patch_api(mocker)
    registry = parse_spec(FAKE_SCHEMA)

    async def main():
        app = DokliApp(config=_config())
        async with app.run_test() as pilot:
            await _mount_browser(app, pilot, _connection(), registry)
            labels = _current_labels(app)
            assert any("project" in label for label in labels)
            assert any("server" in label for label in labels)

    _run(main())


def test_browser_drills_into_records(mocker):
    """We expect drilling into an entity to load its records."""
    _patch_api(mocker)
    registry = parse_spec(FAKE_SCHEMA)

    async def main():
        app = DokliApp(config=_config())
        async with app.run_test() as pilot:
            await _mount_browser(app, pilot, _connection(), registry)
            _select(app, "project")
            await pilot.pause()
            await pilot.press("enter")
            await _wait_for_label(app, pilot, "media")

    _run(main())


def test_browser_drills_into_children(mocker):
    """We expect drilling into a record to show its nested children."""
    _patch_api(mocker)
    registry = parse_spec(FAKE_SCHEMA)

    async def main():
        app = DokliApp(config=_config())
        async with app.run_test() as pilot:
            await _mount_browser(app, pilot, _connection(), registry)
            _select(app, "project")
            await pilot.pause()
            await pilot.press("enter")
            await _wait_for_label(app, pilot, "media")
            _select(app, "media")
            await pilot.pause()
            await pilot.press("enter")
            await _wait_for_label(app, pilot, "production")

    _run(main())


def test_browser_action_key_opens_form(mocker):
    """We expect a generated keybinding to open the action form."""
    _patch_api(mocker)
    registry = parse_spec(FAKE_SCHEMA)

    async def main():
        app = DokliApp(config=_config())
        async with app.run_test() as pilot:
            await _mount_browser(app, pilot, _connection(), registry)
            _select(app, "project")
            await pilot.pause()
            await pilot.press("enter")
            await _wait_for_label(app, pilot, "media")
            await pilot.press("c")
            await pilot.pause()
            assert isinstance(app.screen, ActionFormScreen)

    _run(main())


async def _select_connection(app, pilot):
    list_view = app.screen.query_one("#connections-list")
    list_view.index = 0
    list_view.focus()
    await pilot.pause()
    await pilot.press("enter")
    await pilot.pause()


def test_connection_selection_opens_browser(mocker):
    """We expect selecting a connection to open the browser."""
    _patch_api(mocker)

    async def main():
        app = DokliApp(config=_config())
        async with app.run_test() as pilot:
            await pilot.pause()
            await _select_connection(app, pilot)
            assert isinstance(app.screen, BrowserScreen)

    _run(main())
