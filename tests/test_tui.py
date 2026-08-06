"""TUI tests (browser navigation, forms, wizard)."""

import asyncio

import httpx
from textual.command import CommandPalette
from textual.containers import VerticalScroll
from textual.widgets import Label

from dokli.config import Config, ConnectionConfig
from dokli.tui.app import DokliApp, DokliCommands
from dokli.tui.engine import build_form_model, clear_probe_cache, parse_spec, probe_entity, record_title
from dokli.tui.engine.spec import Entity, EntityAction
from dokli.tui.forms import Form, SelectControl, SwitchControl, TextAreaControl
from dokli.tui.screens.connections import ConnectionsScreen
from dokli.tui.screens.generic.browser import BrowserScreen, Level
from dokli.tui.screens.generic.confirm import ConfirmScreen
from dokli.tui.screens.generic.form import ActionFormScreen
from dokli.tui.screens.generic.help import HelpScreen
from dokli.tui.screens.generic.picker import PickerScreen
from dokli.tui.screens.generic.result import ResultScreen
from dokli.tui.screens.generic.wizard import WizardScreen

FAKE_SCHEMA = {
    "paths": {
        "/auditLog.all": {"get": {}},
        "/project.all": {"get": {}},
        "/project.homeStats": {"get": {}},
        "/project.one": {"get": {"parameters": [{"name": "projectId", "in": "query", "required": True}]}},
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
        "/project.update": {
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
        "/environment.one": {"get": {"parameters": [{"name": "environmentId", "in": "query", "required": True}]}},
        "/compose.one": {"get": {"parameters": [{"name": "composeId", "in": "query", "required": True}]}},
        "/compose.update": {
            "post": {
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "sourceType": {"type": "string", "enum": ["raw", "github"]},
                                    "composeType": {"type": "string", "enum": ["docker-compose", "stack"]},
                                    "composeFile": {"type": "string"},
                                    "name": {"type": "string"},
                                },
                                "required": ["name"],
                            }
                        }
                    }
                }
            }
        },
        "/compose.readLogs": {
            "get": {
                "parameters": [
                    {"name": "composeId", "in": "query", "required": True},
                    {"name": "containerId", "in": "query", "required": True},
                    {"name": "tail", "in": "query"},
                    {"name": "since", "in": "query"},
                    {"name": "search", "in": "query"},
                ]
            }
        },
        "/application.readLogs": {
            "get": {
                "parameters": [
                    {"name": "applicationId", "in": "query", "required": True},
                    {"name": "tail", "in": "query"},
                ]
            }
        },
        "/docker.getContainersByAppNameMatch": {
            "get": {
                "parameters": [
                    {"name": "appName", "in": "query", "required": True},
                    {"name": "appType", "in": "query"},
                    {"name": "serverId", "in": "query"},
                ]
            }
        },
        "/server.all": {"get": {}},
    }
}


class FakeResponse:
    """Minimal response stand-in."""

    def __init__(self, data, status_code: int = 200):
        self._data = data
        self.status_code = status_code

    def json(self):
        return self._data


def _connection() -> ConnectionConfig:
    return ConnectionConfig(name="test-env", url="https://example.com", api_key_cmd="echo key")


def _config() -> Config:
    return Config(connections=[_connection()])


def _fake_requests():
    return {
        "project.all": [{"projectId": "p1", "name": "media"}, {"projectId": "p2", "name": "services"}],
        "project.homeStats": {
            "projects": 6,
            "compose": 10,
            "services": 10,
            "status": {"running": 8, "idle": 2},
        },
        "project.one": {
            "projectId": "p1",
            "name": "media",
            "environments": [{"environmentId": "e1", "name": "production", "isDefault": True}],
        },
        "environment.one": {
            "environmentId": "e1",
            "name": "production",
            "compose": [{"composeId": "c1", "name": "torrents"}],
        },
        "compose.one": {
            "composeId": "c1",
            "name": "torrents",
            "appName": "media-torrents-abc123",
            "composeType": "docker-compose",
            "sourceType": "raw",
            "composeFile": "version: '3'",
        },
        "docker.getContainersByAppNameMatch": [
            {"containerId": "cc1", "name": "frigate", "state": "running", "status": "Up 8 weeks"},
            {"containerId": "cc2", "name": "frigate-notify", "state": "running", "status": "Up 8 weeks"},
        ],
        "compose.readLogs": "2026-08-05T19:55:54Z frigate started",
    }


def _patch_api(mocker):
    client = mocker.Mock()
    responses = _fake_requests()
    clear_probe_cache("test-env")

    def fake_request(method, path, params):
        return FakeResponse(responses.get(path, []))

    client.request.side_effect = fake_request
    mocker.patch("dokli.tui.screens.generic.browser.APIClient", return_value=client)
    mocker.patch("dokli.tui.app.APIClient", return_value=mocker.Mock(schema=FAKE_SCHEMA))
    return responses


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
    index = next(i for i, item in enumerate(screen.current.items) if record_title(item) == label)
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
    model = build_form_model({"properties": {"description": {"type": "string"}, "name": {"type": "string"}}})
    form = Form.from_model(model, data={"description": "line1\nline2"})
    assert isinstance(form.fields["description"], TextAreaControl)
    assert form.fields["description"].get_data() == "line1\nline2"
    assert not isinstance(form.fields["name"], TextAreaControl)


def test_textarea_typing_is_not_reversed(mocker):
    """We expect typing into a text area to keep the natural character order."""
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
            area = screen.form.fields["description"]
            assert isinstance(area, TextAreaControl)
            area.query_one("#description-input").focus()
            await pilot.pause()
            for ch in "Proxy":
                await pilot.press(ch)
            await pilot.pause()
            assert area.value == "Proxy"

    _run(main())


def test_empty_optional_fields_do_not_error(mocker):
    """We expect empty optional fields (selects, numbers, lists) not to error on validate."""
    schema = {
        "paths": {
            "/x.update": {
                "post": {
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "mode": {"type": "string", "enum": ["a", "b"]},
                                        "count": {"type": "integer"},
                                        "tags": {"type": "array"},
                                    },
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    mocker.patch("dokli.tui.app.APIClient")
    mocker.patch("dokli.tui.screens.generic.execute.APIClient")
    registry = parse_spec(schema)
    action = registry.get("x").get("update")

    async def main():
        app = DokliApp(config=_config())
        async with app.run_test() as pilot:
            screen = ActionFormScreen(_connection(), action)
            app.install_screen(screen, name="form")
            app.push_screen("form")
            await pilot.pause()
            await pilot.pause()
            assert screen.form.validate() is True
            assert not any(ctrl.error for ctrl in screen.form.fields.values())

    _run(main())


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


def test_filter_enter_confirms_and_keeps_filter(mocker):
    """We expect Enter in the filter to close it and keep the filter applied."""
    _patch_api(mocker)
    registry = parse_spec(FAKE_SCHEMA)

    async def main():
        app = DokliApp(config=_config())
        async with app.run_test() as pilot:
            await _mount_browser(app, pilot, _connection(), registry)
            await pilot.press("/")
            await pilot.pause()
            filter_input = app.screen.query_one("#filter")
            assert app.screen.focused is filter_input
            filter_input.value = "project"
            await pilot.pause()
            await pilot.press("enter")
            await pilot.pause()
            assert filter_input.display is False
            labels = _current_labels(app)
            assert any("project" in label for label in labels)
            assert not any("server" in label for label in labels)

    _run(main())


def test_filter_navigation_stays_in_filtered_list(mocker):
    """We expect navigation and drill to use the filtered list, not the full one."""
    _patch_api(mocker)
    registry = parse_spec(FAKE_SCHEMA)

    async def main():
        app = DokliApp(config=_config())
        async with app.run_test() as pilot:
            await _mount_browser(app, pilot, _connection(), registry)
            await pilot.press("/")
            await pilot.pause()
            filter_input = app.screen.query_one("#filter")
            filter_input.value = "pro"
            await pilot.pause()
            await pilot.press("enter")
            await pilot.pause()
            labels = _current_labels(app)
            assert len(labels) == 1 and "project" in labels[0]
            screen = app.screen
            index_before = screen.current.index
            await pilot.press("j")
            await pilot.pause()
            assert screen.current.index == index_before  # clamped to the filtered list
            await pilot.press("enter")
            await _wait_for_label(app, pilot, "media")

    _run(main())


def test_filter_reset_after_drill(mocker):
    """We expect the filter to reset when navigating to a new level."""
    _patch_api(mocker)
    registry = parse_spec(FAKE_SCHEMA)

    async def main():
        app = DokliApp(config=_config())
        async with app.run_test() as pilot:
            await _mount_browser(app, pilot, _connection(), registry)
            await pilot.press("/")
            await pilot.pause()
            filter_input = app.screen.query_one("#filter")
            filter_input.value = "pro"
            await pilot.pause()
            await pilot.press("enter")
            await pilot.pause()
            assert len(_current_labels(app)) == 1
            await pilot.press("enter")
            await _wait_for_label(app, pilot, "media")
            labels = _current_labels(app)
            assert any("media" in label for label in labels)
            assert any("services" in label for label in labels)
            assert app.screen._filter == ""

    _run(main())


def test_update_form_enriches_record_via_one(mocker):
    """We expect opening an update form to enrich the record via one."""
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
            _select(app, "production")
            await pilot.pause()
            await pilot.press("enter")
            await _wait_for_label(app, pilot, "torrents")
            await pilot.press("u")
            await pilot.pause()
            await pilot.pause()
            assert isinstance(app.screen, ActionFormScreen)
            form = app.screen.form
            assert form.fields["sourceType"].value == "raw"
            assert form.fields["composeFile"].value == "version: '3'"

    _run(main())


def test_browser_reloads_current_level_after_action(mocker):
    """We expect the current level to reload when resuming after an action."""
    responses = _patch_api(mocker)
    registry = parse_spec(FAKE_SCHEMA)

    async def main():
        app = DokliApp(config=_config())
        async with app.run_test() as pilot:
            await _mount_browser(app, pilot, _connection(), registry)
            _select(app, "project")
            await pilot.pause()
            await pilot.press("enter")
            await _wait_for_label(app, pilot, "media")
            assert any("media" in label for label in _current_labels(app))
            responses["project.all"] = [
                {"projectId": "p1", "name": "media"},
                {"projectId": "p3", "name": "brand-new"},
            ]
            app.screen.on_screen_resume(None)
            await _wait_for_label(app, pilot, "brand-new")

    _run(main())


def test_create_form_opens_empty(mocker):
    """We expect a create action to open an empty form, not prefilled."""
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
            await pilot.pause()
            assert isinstance(app.screen, ActionFormScreen)
            form = app.screen.form
            assert form.fields["name"].value == ""

    _run(main())


def test_query_action_shows_result(mocker):
    """We expect a GET action to show its result in a result screen."""
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
            await pilot.press("o")
            await pilot.pause()
            await pilot.pause()
            assert isinstance(app.screen, ResultScreen)
            text = "\n".join(str(label.renderable) for label in app.screen.query_one("#result-scroll").children)
            assert "Projects" in text
            assert "Compose" in text
            assert "Running" in text

    _run(main())


def test_result_search_highlights_and_navigates(mocker):
    """We expect / to open a search that counts matches and navigates with n/N."""
    mocker.patch("dokli.tui.app.APIClient")
    registry = parse_spec(FAKE_SCHEMA)
    action = registry.get("project").get("homeStats")
    logs = "\n".join(f"2026-08-05 line {i} GET /api/projects" for i in range(5))

    async def main():
        app = DokliApp(config=_config())
        async with app.run_test() as pilot:
            screen = ResultScreen(_connection(), action, logs)
            app.install_screen(screen, name="result")
            app.push_screen("result")
            await pilot.pause()
            await pilot.pause()
            # no matches query
            await pilot.press("/")
            await pilot.pause()
            await pilot.press(*"zzz")
            await pilot.pause()
            await pilot.pause()
            assert str(screen.query_one("#match-status", Label).renderable) == "No matches"
            await pilot.press("escape")
            await pilot.pause()
            await pilot.press("/")
            await pilot.pause()
            await pilot.press(*"api")
            await pilot.pause()
            await pilot.pause()
            assert str(screen.query_one("#match-status", Label).renderable) == "1/5 matches"
            # commit search (blur) then navigate
            await pilot.press("enter")
            await pilot.pause()
            await pilot.press("n")
            await pilot.pause()
            await pilot.pause()
            assert str(screen.query_one("#match-status", Label).renderable) == "2/5 matches"
            await pilot.press("N")
            await pilot.pause()
            await pilot.pause()
            assert str(screen.query_one("#match-status", Label).renderable) == "1/5 matches"

    _run(main())


def test_result_search_escape_clears(mocker):
    """We expect escape to clear the search and restore the plain result."""
    mocker.patch("dokli.tui.app.APIClient")
    registry = parse_spec(FAKE_SCHEMA)
    action = registry.get("project").get("homeStats")
    logs = "\n".join(f"2026-08-05 line {i} GET /api/projects" for i in range(3))

    async def main():
        app = DokliApp(config=_config())
        async with app.run_test() as pilot:
            screen = ResultScreen(_connection(), action, logs)
            app.install_screen(screen, name="result")
            app.push_screen("result")
            await pilot.pause()
            await pilot.pause()
            await pilot.press("/")
            await pilot.pause()
            await pilot.press(*"api")
            await pilot.pause()
            await pilot.pause()
            assert str(screen.query_one("#match-status", Label).renderable) == "1/3 matches"
            await pilot.press("escape")
            await pilot.pause()
            await pilot.pause()
            assert str(screen.query_one("#match-status", Label).renderable) == ""
            assert isinstance(app.screen, ResultScreen)

    _run(main())


def test_result_refresh_refetches(mocker):
    """We expect r to re-run the action with the original params and update the result."""
    mocker.patch("dokli.tui.app.APIClient")
    registry = parse_spec(FAKE_SCHEMA)
    action = registry.get("project").get("homeStats")
    params = {"projectId": "p1"}

    def fake_request(method, path, params_):
        return FakeResponse({"projects": 99, "status": {"running": 1, "idle": 0}})

    client = mocker.Mock()
    client.request.side_effect = fake_request
    mocker.patch("dokli.tui.screens.generic.result.APIClient", return_value=client)

    async def main():
        app = DokliApp(config=_config())
        async with app.run_test() as pilot:
            screen = ResultScreen(_connection(), action, {"projects": 0}, params=params)
            app.install_screen(screen, name="result")
            app.push_screen("result")
            await pilot.pause()
            await pilot.pause()
            await pilot.press("f5")
            await pilot.pause()
            await pilot.pause()
            client.request.assert_called_once_with("GET", action.route, params)
            text = "\n".join(
                str(label.renderable)
                for label in screen.query_one("#result-scroll").children
                if isinstance(label, Label)
            )
            assert "99" in text

    _run(main())


def test_read_logs_params_only_backfill_entity_id(mocker):
    """We expect GET params to backfill only the entity's own id, never other params."""
    _patch_api(mocker)
    registry = parse_spec(FAKE_SCHEMA)

    async def main():
        app = DokliApp(config=_config())
        async with app.run_test() as pilot:
            await _mount_browser(app, pilot, _connection(), registry)
            screen = app.screen
            action = registry.get("application").get("readLogs")
            screen.path = [
                Level(
                    kind="children",
                    items=[{"_kind": "application", "applicationId": "a1", "name": "web"}],
                    entity="application",
                )
            ]
            screen.current.index = 0
            await screen._show_result(action)
            await pilot.pause()
            assert isinstance(app.screen, ResultScreen)
            _, _, params = screen.client.request.call_args.args
            assert params == {"applicationId": "a1"}
            # the result screen must keep the params so its refresh re-uses them
            assert app.screen.params == {"applicationId": "a1"}

    _run(main())


def test_read_logs_opens_picker_for_container_id(mocker):
    """We expect compose.readLogs to open a container picker when containerId
    is missing from the record, then run with the chosen container.
    """
    responses = _patch_api(mocker)
    registry = parse_spec(FAKE_SCHEMA)

    async def main():
        app = DokliApp(config=_config())
        async with app.run_test() as pilot:
            await _mount_browser(app, pilot, _connection(), registry)
            screen = app.screen
            action = registry.get("compose").get("readLogs")
            screen.path = [
                Level(
                    kind="children",
                    items=[{"_kind": "compose", "composeId": "c1", "name": "torrents"}],
                    entity="compose",
                )
            ]
            screen.current.index = 0
            worker = screen.run_worker(screen._show_result(action), group="test")
            await pilot.pause()
            assert isinstance(app.screen, PickerScreen)
            labels = [
                str(label.renderable)
                for label in app.screen.query_one("#picker-list", VerticalScroll).children
                if isinstance(label, Label)
            ]
            assert any("frigate" in label for label in labels)
            # pick the first container
            await pilot.press("enter")
            for _ in range(30):
                await pilot.pause()
                if isinstance(app.screen, ResultScreen):
                    break
            assert isinstance(app.screen, ResultScreen)
            await worker.wait()
            calls = screen.client.request.call_args_list
            params = calls[-1][0][2]
            assert params["composeId"] == "c1"
            assert params["containerId"] in ("cc1", "cc2")

    _run(main())


def test_read_logs_no_candidates_notifies(mocker):
    """We expect a notify (not a request) when no containers are available."""
    responses = _patch_api(mocker)
    responses["docker.getContainersByAppNameMatch"] = []
    registry = parse_spec(FAKE_SCHEMA)

    async def main():
        app = DokliApp(config=_config())
        async with app.run_test() as pilot:
            await _mount_browser(app, pilot, _connection(), registry)
            screen = app.screen
            screen.notify = mocker.Mock()
            action = registry.get("compose").get("readLogs")
            screen.path = [
                Level(
                    kind="children",
                    items=[{"_kind": "compose", "composeId": "c1", "name": "torrents"}],
                    entity="compose",
                )
            ]
            screen.current.index = 0
            await screen._show_result(action)
            screen.notify.assert_called_once()
            assert "No Containers" in screen.notify.call_args.args[0]
            assert not any(call[0][1] == "compose.readLogs" for call in screen.client.request.call_args_list)

    _run(main())


def test_detail_shows_related_containers(mocker):
    """We expect the detail pane to list related containers for a compose record."""
    _patch_api(mocker)
    registry = parse_spec(FAKE_SCHEMA)

    async def main():
        app = DokliApp(config=_config())
        async with app.run_test() as pilot:
            await _mount_browser(app, pilot, _connection(), registry)
            screen = app.screen
            screen.path = [
                Level(
                    kind="children",
                    items=[{"_kind": "compose", "composeId": "c1", "name": "torrents"}],
                    entity="compose",
                )
            ]
            screen.current.index = 0
            await screen._refresh_all()
            await pilot.pause()
            detail = [
                str(label.renderable)
                for label in screen.query_one("#detail-pane", VerticalScroll).children
                if isinstance(label, Label)
            ]
            assert any("Containers (2)" in label for label in detail)
            assert any("frigate" in label for label in detail)

    _run(main())


def test_related_containers_enrich_via_one(mocker):
    """We expect the browser to enrich a compose record via one to get the docker
    project name (appName) and appType before fetching its containers."""
    _patch_api(mocker)
    registry = parse_spec(FAKE_SCHEMA)

    async def main():
        app = DokliApp(config=_config())
        async with app.run_test() as pilot:
            await _mount_browser(app, pilot, _connection(), registry)
            screen = app.screen
            screen.path = [
                Level(
                    kind="children",
                    items=[{"_kind": "compose", "composeId": "c1", "name": "torrents"}],
                    entity="compose",
                )
            ]
            screen.current.index = 0
            related = screen._related_records(screen.selected)
            docker_call = next(
                call
                for call in screen.client.request.call_args_list
                if call[0][1] == "docker.getContainersByAppNameMatch"
            )
            _, _, params = docker_call.args
            assert params["appName"] == "media-torrents-abc123"
            assert params["appType"] == "docker-compose"
            assert [r["name"] for r in related] == ["frigate", "frigate-notify"]

    _run(main())


def test_unusable_entities_are_hidden(mocker):
    """We expect entities whose all action returns 403 to be hidden."""
    import httpx

    clear_probe_cache("test-env")
    client = mocker.Mock()
    responses = _fake_requests()

    def fake_request(method, path, params):
        if path == "auditLog.all":
            request = httpx.Request("GET", "https://example.com/api/auditLog.all")
            response = httpx.Response(403, request=request)
            raise httpx.HTTPStatusError("403 Forbidden", request=request, response=response)
        return FakeResponse(responses.get(path, []))

    client.request.side_effect = fake_request
    mocker.patch("dokli.tui.screens.generic.browser.APIClient", return_value=client)
    mocker.patch("dokli.tui.app.APIClient", return_value=mocker.Mock(schema=FAKE_SCHEMA))
    registry = parse_spec(FAKE_SCHEMA)

    async def main():
        app = DokliApp(config=_config())
        async with app.run_test() as pilot:
            await _mount_browser(app, pilot, _connection(), registry)
            for _ in range(30):
                await pilot.pause()
                labels = _current_labels(app)
                if "auditLog" not in labels and any("project" in label for label in labels):
                    break
            labels = _current_labels(app)
            assert not any("auditLog" in label for label in labels)
            assert any("project" in label for label in labels)

    _run(main())


def test_probe_entity(mocker):
    """We expect probe_entity to distinguish usable and gated endpoints."""
    import httpx

    def action():
        return EntityAction(verb="all", method="GET", route="x.all")

    ok_client = mocker.Mock()
    ok_client.request.return_value = FakeResponse([], status_code=200)
    assert probe_entity(ok_client, Entity(name="x", actions={"all": action()})) is True

    forbidden_client = mocker.Mock()

    def raise_403(method, path, params):
        request = httpx.Request("GET", "https://example.com/api/x.all")
        response = httpx.Response(403, request=request)
        raise httpx.HTTPStatusError("403 Forbidden", request=request, response=response)

    forbidden_client.request.side_effect = raise_403
    assert probe_entity(forbidden_client, Entity(name="x", actions={"all": action()})) is False

    def raise_transport(method, path, params):
        raise httpx.ConnectError("connection refused", request=httpx.Request("GET", "https://example.com/api/x.all"))

    transport_client = mocker.Mock()
    transport_client.request.side_effect = raise_transport
    assert probe_entity(transport_client, Entity(name="x", actions={"all": action()})) is True


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


def test_connection_argument_opens_browser_directly(mocker):
    """We expect DokliApp(connection=...) to open the browser directly on mount."""
    _patch_api(mocker)

    async def main():
        app = DokliApp(config=_config(), connection=_connection())
        async with app.run_test() as pilot:
            for _ in range(30):
                await pilot.pause()
                if isinstance(app.screen, BrowserScreen):
                    break
            assert isinstance(app.screen, BrowserScreen)
            assert app.connection is not None
            assert app.connection.name == "test-env"

    _run(main())


def test_connection_argument_unreachable_falls_back(mocker):
    """We expect an unreachable connection to fall back to the connections screen."""
    error = httpx.ConnectError("boom", request=httpx.Request("GET", "https://example.com/"))
    mocker.patch("dokli.tui.app.APIClient", side_effect=error)

    async def main():
        app = DokliApp(config=_config(), connection=_connection())
        async with app.run_test() as pilot:
            for _ in range(30):
                await pilot.pause()
                if isinstance(app.screen, ConnectionsScreen):
                    break
            assert isinstance(app.screen, ConnectionsScreen)

    _run(main())


# -- connections persistence ------------------------------------------------


def test_add_connection_persists(mocker):
    """We expect a new connection to be added to the config and saved."""
    config = _config()
    save = mocker.patch("dokli.config.Config.save")
    new_connection = ConnectionConfig(name="stage", url="https://stage.example.com", api_key_cmd="echo key")

    async def main():
        app = DokliApp(config=config)
        async with app.run_test() as pilot:
            await pilot.pause()
            app.on_connections_screen_add_connection(ConnectionsScreen.AddConnection(connection=new_connection))
            assert any(c.name == "stage" for c in app.config.connections)
            save.assert_called_once()

    _run(main())


def test_update_connection_persists(mocker):
    """We expect an edited connection to replace the existing one and be saved."""
    config = _config()
    save = mocker.patch("dokli.config.Config.save")
    updated = ConnectionConfig(name="test-env", url="https://other.example.com", api_key_cmd="echo key")

    async def main():
        app = DokliApp(config=config)
        async with app.run_test() as pilot:
            await pilot.pause()
            app.on_connections_screen_update_connection(ConnectionsScreen.UpdateConnection(connection=updated))
            assert app.config.connections[0].url.host == "other.example.com"
            assert len(app.config.connections) == 1
            save.assert_called_once()

    _run(main())


def test_delete_connection_persists(mocker):
    """We expect a deleted connection to be removed from the config and saved."""
    config = _config()
    save = mocker.patch("dokli.config.Config.save")

    async def main():
        app = DokliApp(config=config)
        async with app.run_test() as pilot:
            await pilot.pause()
            app.on_connections_screen_delete_connection(ConnectionsScreen.DeleteConnection(connection=_connection()))
            assert app.config.connections == []
            save.assert_called_once()

    _run(main())


def test_rename_connection_replaces_not_duplicates(mocker):
    """We expect renaming a connection to replace it, not duplicate it."""
    config = _config()
    save = mocker.patch("dokli.config.Config.save")
    renamed = ConnectionConfig(name="renamed", url="https://other.example.com", api_key_cmd="echo key")

    async def main():
        app = DokliApp(config=config)
        async with app.run_test() as pilot:
            await pilot.pause()
            app.on_connections_screen_update_connection(
                ConnectionsScreen.UpdateConnection(connection=renamed, original=_connection())
            )
            assert [c.name for c in app.config.connections] == ["renamed"]
            save.assert_called_once()

    _run(main())


def test_connection_edit_syncs_screen(mocker):
    """We expect the connections screen list to refresh after an edit."""
    config = _config()
    save = mocker.patch("dokli.config.Config.save")
    updated = ConnectionConfig(name="test-env", url="https://other.example.com", api_key_cmd="echo key")

    async def main():
        app = DokliApp(config=config)
        async with app.run_test() as pilot:
            await pilot.pause()
            assert isinstance(app.screen, ConnectionsScreen)
            app.on_connections_screen_update_connection(
                ConnectionsScreen.UpdateConnection(connection=updated, original=_connection())
            )
            await pilot.pause()
            assert app.screen.connections[0].url.host == "other.example.com"
            save.assert_called_once()

    _run(main())


# -- help + command palette -------------------------------------------------


def test_help_screen_shows_bindings(mocker):
    """We expect ? to open the help screen listing the keybindings."""
    _patch_api(mocker)

    async def main():
        app = DokliApp(config=_config(), connection=_connection())
        async with app.run_test() as pilot:
            for _ in range(30):
                await pilot.pause()
                if isinstance(app.screen, BrowserScreen):
                    break
            # select 'project' so its contextual actions are available
            screen = app.screen
            vis = screen._visible_items(screen.current)
            screen.current.index = next(
                i for i, item in enumerate(vis) if item.get("name") == "project"
            )
            await pilot.pause()
            await pilot.press("?")
            for _ in range(10):
                await pilot.pause()
                if isinstance(app.screen, HelpScreen):
                    break
            assert isinstance(app.screen, HelpScreen)
            text = "\n".join(
                str(label.renderable)
                for label in app.screen.query_one("#help-scroll").children
                if isinstance(label, Label)
            )
            assert "Quit" in text
            assert "Connections" in text
            # contextual action of the selected entity is listed
            assert "create project" in text

    _run(main())


def test_help_default_bindings_win_over_contextual():
    """We expect default keybindings to win over contextual ones on collision."""
    from dokli.tui.screens.generic.help import _merge_entries

    default = [("c", "Copy"), ("r", "Refresh")]
    contextual = [("r", "Run redeploy on app"), ("x", "Deploy")]
    merged = _merge_entries(default, contextual)
    assert merged == [("c", "Copy"), ("r", "Refresh"), ("x", "Deploy")]


def test_command_palette_opens(mocker):
    """We expect the command palette to open on ctrl+p."""
    _patch_api(mocker)

    async def main():
        app = DokliApp(config=_config())
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("ctrl+p")
            await pilot.pause()
            assert isinstance(app.screen, CommandPalette)

    _run(main())


def test_command_provider_lists_connections(mocker):
    """We expect the command palette provider to offer connections and core commands."""
    _patch_api(mocker)

    async def main():
        app = DokliApp(config=_config())
        async with app.run_test() as pilot:
            await pilot.pause()
            provider = DokliCommands(app.screen)
            hits = [hit async for hit in provider.discover()]
            names = [hit.text for hit in hits]
            assert "Open test-env" in names
            assert "Help" in names
            assert "Quit" in names
            by_name = {hit.text: hit.help for hit in hits}
            assert by_name["Toggle dark mode"] == "[D] Switch between light and dark themes"
            assert by_name["Help"] == "[?] Show the keybindings"

    _run(main())


def test_command_provider_lists_browser_actions(mocker):
    """We expect the palette to expose the selected entity's available actions in the browser."""
    _patch_api(mocker)
    registry = parse_spec(FAKE_SCHEMA)

    async def main():
        app = DokliApp(config=_config())
        async with app.run_test() as pilot:
            await _mount_browser(app, pilot, _connection(), registry)
            _select(app, "project")
            await pilot.pause()
            provider = DokliCommands(app.screen)
            hits = [hit async for hit in provider.discover()]
            names = [hit.text for hit in hits]
            assert "Run create on project" in names
            assert "Run homeStats on project" in names
            assert not any(name == "Run remove on project" for name in names)
            create_help = next(hit.help for hit in hits if hit.text == "Run create on project")
            assert create_help == "[c] create · project (POST)"

    _run(main())


def test_command_provider_lists_form_commands(mocker):
    """We expect the palette to expose form actions when a form is focused."""
    mocker.patch("dokli.tui.app.APIClient")
    registry = parse_spec(FAKE_SCHEMA)
    action = registry.get("project").get("create")

    async def main():
        app = DokliApp(config=_config())
        async with app.run_test() as pilot:
            screen = ActionFormScreen(_connection(), action)
            app.install_screen(screen, name="form")
            app.push_screen("form")
            await pilot.pause()
            provider = DokliCommands(app.screen)
            hits = [hit async for hit in provider.discover()]
            names = [hit.text for hit in hits]
            assert "Submit form" in names
            assert "Wizard mode" in names

    _run(main())


def test_palette_runs_update_action(mocker):
    """We expect an action chosen from the palette to run after the palette closes."""
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
            await pilot.press("ctrl+p")
            for _ in range(10):
                await pilot.pause()
            await pilot.press(*"run update")
            for _ in range(15):
                await pilot.pause()
            await pilot.press("enter")
            for _ in range(5):
                await pilot.pause()
            await pilot.press("enter")
            for _ in range(30):
                await pilot.pause()
                if isinstance(app.screen, ActionFormScreen):
                    break
            assert isinstance(app.screen, ActionFormScreen)

    _run(main())
