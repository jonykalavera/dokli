"""TUI tests (browser navigation, forms, wizard)."""

import asyncio
import threading
import time

import httpx
from textual.command import CommandPalette
from textual.containers import VerticalScroll
from textual.widgets import Input, Label, Static, Switch

from dokli.config import Config, ConnectionConfig, TuiConfig, TuiKeysConfig
from dokli.tui.app import DokliApp, DokliCommands
from dokli.tui.engine import build_form_model, parse_spec, record_title
from dokli.tui.engine.spec import Entity, EntityAction, key_for_verb, sort_entities
from dokli.tui.forms import Form, SelectControl, SwitchControl, TextAreaControl
from dokli.tui.screens.connections import ConnectionsScreen
from dokli.tui.screens.connection import ConnectionScreen
from dokli.tui.screens.generic.browser import BrowserScreen, Level
from dokli.tui.screens.generic.confirm import ConfirmScreen
from dokli.tui.screens.generic.form import ActionFormScreen
from dokli.tui.screens.generic.help import HelpScreen
from dokli.tui.screens.generic.picker import PickerScreen
from dokli.tui.screens.generic.result import ResultScreen, _log_line_text, _timestamp_of
from dokli.tui.screens.generic.wizard import WizardScreen
from dokli.tui.screens.splash import SPINNER_FRAMES, SplashScreen

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
        "/docker.getStackContainersByAppName": {
            "get": {
                "parameters": [
                    {"name": "appName", "in": "query", "required": True},
                    {"name": "serverId", "in": "query"},
                ]
            }
        },
        "/docker.restartContainer": {
            "post": {
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {"containerId": {"type": "string"}, "serverId": {"type": "string"}},
                                "required": ["containerId"],
                            }
                        }
                    }
                }
            }
        },
        "/domain.create": {
            "post": {
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "host": {"type": "string"},
                                    "composeId": {"type": "string"},
                                    "applicationId": {"type": "string"},
                                    "domainType": {"type": "string", "enum": ["application", "compose"]},
                                },
                                "required": ["host"],
                            }
                        }
                    }
                }
            }
        },
        "/domain.update": {
            "post": {
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "host": {"type": "string"},
                                    "domainId": {"type": "string"},
                                    "composeId": {"type": "string"},
                                    "applicationId": {"type": "string"},
                                },
                                "required": ["host", "domainId"],
                            }
                        }
                    }
                }
            }
        },
        "/application.update": {
            "post": {
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "applicationId": {"type": "string"},
                                    "environmentId": {"type": "string"},
                                    "githubId": {"type": "string"},
                                    "dockerImage": {"type": "string"},
                                },
                            }
                        }
                    }
                }
            }
        },
        "/deployment.all": {
            "get": {
                "parameters": [
                    {"name": "applicationId", "in": "query", "required": True},
                ]
            }
        },
        "/deployment.allByCompose": {
            "get": {
                "parameters": [
                    {"name": "composeId", "in": "query", "required": True},
                ]
            }
        },
        "/deployment.allCentralized": {"get": {}},
        "/deployment.readLogs": {
            "get": {
                "parameters": [
                    {"name": "deploymentId", "in": "query", "required": True},
                    {"name": "tail", "in": "query"},
                ]
            }
        },
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
            "domains": [],
            "mounts": [],
        },
        "docker.getContainersByAppNameMatch": [
            {"containerId": "cc1", "name": "frigate", "state": "running", "status": "Up 8 weeks"},
            {"containerId": "cc2", "name": "frigate-notify", "state": "running", "status": "Up 8 weeks"},
        ],
        "docker.getStackContainersByAppName": [
            {"containerId": "sc1", "name": "stack-svc", "state": "running", "status": "Up 2 days"},
        ],
        "compose.readLogs": "2026-08-05T19:55:54Z frigate started",
        "deployment.allCentralized": [
            {"deploymentId": "d1", "name": "media-torrents-abc123", "status": "running"},
        ],
        "deployment.allByCompose": [
            {"deploymentId": "d1", "name": "media-torrents-abc123", "status": "running"},
        ],
        "deployment.readLogs": "2026-08-05T20:00:00Z deployment started",
    }


def _patch_api(mocker):
    client = mocker.Mock(schema=FAKE_SCHEMA)
    responses = _fake_requests()

    def fake_request(method, path, params):
        return FakeResponse(responses.get(path, []))

    client.request.side_effect = fake_request
    mocker.patch("dokli.tui.screens.generic.browser.APIClient", return_value=client)
    mocker.patch("dokli.tui.app.APIClient", return_value=client)
    mocker.patch("dokli.tui.screens.generic.execute.APIClient", return_value=client)
    mocker.patch("dokli.tui.screens.generic.result.APIClient", return_value=client)
    return responses


def _run(coro):
    return asyncio.run(coro)


async def _mount_browser(app, pilot, connection, registry):
    """Push the browser screen and wait for it to render."""
    screen = BrowserScreen(connection, registry, entity_order=app.config.tui.entity_order)
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


async def _wait_for_browser(app, pilot):
    """Wait for the browser, allowing for the splash minimum duration."""
    for _ in range(100):
        await pilot.pause()
        if isinstance(app.screen, BrowserScreen):
            return
        await asyncio.sleep(0.05)
    raise AssertionError("Browser never appeared")


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


def test_form_surfaces_model_level_errors():
    """We expect a cross-field model error (empty loc) not to crash and to be shown."""
    form = Form.from_model(ConnectionConfig)
    form._set_errors(
        [
            {
                "loc": (),
                "msg": "Must provide api_key, api_key_keyring or api_key_cmd.",
                "type": "value_error",
                "input": {"name": "hot-test", "api_key": None, "api_key_cmd": None},
            }
        ]
    )
    assert form.error == "Must provide api_key, api_key_keyring or api_key_cmd."


def test_connection_form_model_error_no_crash(mocker):
    """We expect typing in a new connection form not to crash on the model validator."""
    mocker.patch("dokli.config.Config.save")

    async def main():
        app = DokliApp(config=_config())
        async with app.run_test() as pilot:
            await pilot.pause()
            screen = app.screen
            screen.action_add_connection()
            for _ in range(10):
                await pilot.pause()
            assert isinstance(app.screen, ConnectionScreen)
            form = app.screen.query_one(Form)
            form.fields["name"].value = "hot-test"
            form.fields["url"].value = "https://storm.example.dev"
            form.fields["notes"].value = "H"
            # keychain is on by default for new connections; turn it off so the
            # form has no credential and the model-level error is exercised.
            form.fields["api_key_keyring"].value = False
            form.validate()
            assert form.error == "Must provide api_key, api_key_keyring or api_key_cmd."
            # typing in notes triggers validation without crashing
            form.fields["notes"].value = "HELLO"
            form.validate()
            assert form.error == "Must provide api_key, api_key_keyring or api_key_cmd."

    _run(main())


def test_connection_form_notes_optional(mocker):
    """We expect an empty notes field not to make the connection form invalid."""
    mocker.patch("dokli.config.Config.save")

    async def main():
        app = DokliApp(config=_config())
        async with app.run_test() as pilot:
            await pilot.pause()
            app.screen.action_add_connection()
            for _ in range(10):
                await pilot.pause()
            form = app.screen.query_one(Form)
            form.fields["name"].value = "hot-test"
            form.fields["url"].value = "https://storm.example.dev"
            form.fields["api_key"].value = "*" * 64
            assert form.validate() is True
            assert form.cleaned_data["notes"] == ""

    _run(main())


def test_connection_form_keyring_default_on_for_new(mocker):
    """We expect new connection forms to default to the keychain (secure by default)."""
    mocker.patch("dokli.config.Config.save")

    async def main():
        app = DokliApp(config=_config())
        async with app.run_test() as pilot:
            await pilot.pause()
            app.screen.action_add_connection()
            for _ in range(10):
                await pilot.pause()
            form = app.screen.query_one(Form)
            assert form.fields["api_key_keyring"].value is True
            assert form.fields["api_key_cmd"].display is False

    _run(main())


def test_connection_form_keyring_toggle_shows_api_key_cmd(mocker):
    """We expect toggling the keychain to hide/show the api_key_cmd field."""
    mocker.patch("dokli.config.Config.save")

    async def main():
        app = DokliApp(config=_config())
        async with app.run_test() as pilot:
            await pilot.pause()
            app.screen.action_add_connection()
            for _ in range(10):
                await pilot.pause()
            form = app.screen.query_one(Form)
            api_key_cmd = form.fields["api_key_cmd"]
            assert api_key_cmd.display is False  # keyring default on for new
            keyring_switch = form.fields["api_key_keyring"].query_one(Switch)
            keyring_switch.value = False
            await pilot.pause()
            assert api_key_cmd.display is True
            keyring_switch.value = True
            await pilot.pause()
            assert api_key_cmd.display is False
            assert api_key_cmd.value is None

    _run(main())


def test_form_validation_is_debounced(mocker):
    """We expect live validation to be debounced so rapid typing does not stall."""
    mocker.patch("dokli.config.Config.save")

    async def main():
        app = DokliApp(config=_config())
        async with app.run_test() as pilot:
            await pilot.pause()
            app.screen.action_add_connection()
            for _ in range(10):
                await pilot.pause()
            form = app.screen.query_one(Form)
            form.fields["name"].query_one(Input).focus()
            await pilot.pause()
            await pilot.press("x")
            await pilot.pause(0.05)
            assert form._validate_timer is not None
            await pilot.pause(0.25)
            assert form._validate_timer is None

    _run(main())


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


def test_browser_respects_verb_key_override(mocker):
    """We expect a configured verb key to replace the default binding."""
    _patch_api(mocker)
    registry = parse_spec(FAKE_SCHEMA)
    config = Config(
        connections=[_connection()],
        tui=TuiConfig(keys=TuiKeysConfig(verbs={"create": "n"})),
    )

    async def main():
        app = DokliApp(config=config)
        async with app.run_test() as pilot:
            await _mount_browser(app, pilot, _connection(), registry)
            _select(app, "project")
            await pilot.pause()
            await pilot.press("enter")
            await _wait_for_label(app, pilot, "media")
            await pilot.press("n")
            await pilot.pause()
            assert isinstance(app.screen, ActionFormScreen)

    _run(main())


def test_app_applies_tui_config():
    """We expect the app to apply the theme, colors and app keys from config."""
    config = Config(
        connections=[_connection()],
        tui=TuiConfig(
            theme="light",
            colors={"primary": "#111111"},
            keys=TuiKeysConfig(app={"connections": "n"}),
        ),
    )
    app = DokliApp(config=config)

    assert app.dark is False
    assert app.design["dark"].primary.hex == "#111111"
    assert app.design["light"].primary.hex == "#111111"
    assert app.app_keys["connections"] == "n"
    assert app.app_keys["toggle_dark"] == "D"
    binding_keys = {binding.key: binding.action for binding in app._bindings.keys.values()}
    assert binding_keys["n"] == "connections"
    assert binding_keys["D"] == "toggle_dark"


def test_structural_colors_follow_active_theme():
    """We expect structural colors to only affect the active theme variant."""
    config = Config(
        connections=[_connection()],
        tui=TuiConfig(theme="dark", colors={"background": "#000000", "primary": "#E4007C"}),
    )
    app = DokliApp(config=config)

    assert app.dark is True
    assert app.design["dark"].primary.hex == "#E4007C"
    assert app.design["light"].primary.hex == "#E4007C"
    assert app.design["dark"].background.hex == "#000000"
    assert app.design["light"].background.hex != "#000000"


def test_entity_and_state_color_overrides():
    """We expect the app to apply entity and container-state color overrides."""
    from dokli.tui.engine.icons import (
        ENTITY_ICON_COLORS,
        entity_icon_color,
        set_entity_color_overrides,
        set_state_color_overrides,
        state_color,
    )

    set_entity_color_overrides({"compose": "#a6e3a1"})
    set_state_color_overrides({"running": "#f9e2af"})
    try:
        assert entity_icon_color("compose") == "#a6e3a1"
        assert entity_icon_color("project") == ENTITY_ICON_COLORS["project"]
        assert state_color("running") == "#f9e2af"
        assert state_color("exited") == "#f38ba8"
    finally:
        set_entity_color_overrides({})
        set_state_color_overrides({})

    config = Config(
        connections=[_connection()],
        tui=TuiConfig(entity_colors={"redis": "#fab387"}, state_colors={"exited": "#f9e2af"}),
    )
    DokliApp(config=config)
    assert entity_icon_color("redis") == "#fab387"
    assert state_color("exited") == "#f9e2af"


def test_mount_refreshes_css_for_custom_design(mocker):
    """We expect mounting to refresh CSS so the custom design applies at startup."""
    _patch_api(mocker)
    config = Config(connections=[_connection()], tui=TuiConfig(colors={"primary": "#E4007C"}))
    app = DokliApp(config=config)
    refresh = mocker.spy(app, "refresh_css")

    async def main():
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.pause()

    _run(main())
    assert refresh.called


def test_key_for_verb_honors_overrides():
    """We expect key_for_verb to respect custom verb and system keys."""
    assert key_for_verb("deploy") == "x"
    assert key_for_verb("deploy", verb_keys={"deploy": "z"}) == "z"
    assert key_for_verb("create", system_keys=frozenset("c")) != "c"


def test_sort_entities_prioritizes():
    """We expect sort_entities to surface priority entities first."""
    names = ["user", "project", "auditLog", "server", "tag"]
    assert sort_entities(names, ("project",)) == ["project", "auditLog", "server", "tag", "user"]
    assert sort_entities(names, ("project", "server")) == ["project", "server", "auditLog", "tag", "user"]
    assert sort_entities(names, ("nope",)) == ["auditLog", "project", "server", "tag", "user"]
    assert sort_entities(names) == ["project", "auditLog", "server", "tag", "user"]


def test_browser_entities_prioritize_project(mocker):
    """We expect the top-level entity list to start with project by default."""
    _patch_api(mocker)
    registry = parse_spec(FAKE_SCHEMA)

    async def main():
        app = DokliApp(config=_config())
        async with app.run_test() as pilot:
            await _mount_browser(app, pilot, _connection(), registry)
            screen = app.screen
            labels = _current_labels(app)
            assert "project" in labels[0]

    _run(main())


def test_browser_respects_entity_order(mocker):
    """We expect a configured entity_order to reorder the top-level list."""
    _patch_api(mocker)
    registry = parse_spec(FAKE_SCHEMA)
    config = Config(connections=[_connection()], tui=TuiConfig(entity_order=["server", "project"]))

    async def main():
        app = DokliApp(config=config)
        async with app.run_test() as pilot:
            await _mount_browser(app, pilot, _connection(), registry)
            screen = app.screen
            labels = _current_labels(app)
            assert "server" in labels[0]
            assert "project" in labels[1]

    _run(main())


def test_connection_opens_browser_after_splash(mocker):
    """We expect a connection to show the splash, then the browser."""
    _patch_api(mocker)

    class SlowClient:
        @property
        def schema(self):
            time.sleep(2)
            return FAKE_SCHEMA

        def request(self, method, path, params):
            return FakeResponse({})

    mocker.patch("dokli.tui.app.APIClient", return_value=SlowClient())

    async def main():
        app = DokliApp(config=_config(), connection=_connection())
        async with app.run_test() as pilot:
            splash_seen = False
            for _ in range(60):
                await pilot.pause()
                if isinstance(app.screen, SplashScreen):
                    splash_seen = True
                    break
            assert splash_seen, "splash never shown"
            await _wait_for_browser(app, pilot)
            assert isinstance(app.screen, BrowserScreen)

    _run(main())


def test_splash_screen_shows_status(mocker):
    """We expect the splash to render the logo, a status box, and accept updates."""
    _patch_api(mocker)

    async def main():
        app = DokliApp(config=_config())
        async with app.run_test() as pilot:
            splash = SplashScreen(classes="Splash")
            app.install_screen(splash, name="splash")
            app.push_screen("splash")
            await pilot.pause()
            assert "splash-logo" in [widget.id for widget in splash.query(Static)]
            assert splash.query_one("#status-panel") is not None
            splash.set_status("Fetching schema…")
            await pilot.pause()
            status = str(splash.query_one("#splash-status", Label).renderable)
            assert status.endswith("Fetching schema…")
            assert status.split()[0] in SPINNER_FRAMES

    _run(main())


def test_api_get_does_not_block_loop(mocker):
    """We expect a slow API call to run off the event loop (UI stays responsive)."""
    _patch_api(mocker)
    registry = parse_spec(FAKE_SCHEMA)
    action = registry.get("project").get("all")

    async def main():
        app = DokliApp(config=_config())
        async with app.run_test() as pilot:
            await _mount_browser(app, pilot, _connection(), registry)
            screen = app.screen
            real_request = screen.client.request

            def slow_request(*args, **kwargs):
                time.sleep(1.5)
                return real_request(*args, **kwargs)

            screen.client.request = slow_request
            task = asyncio.create_task(screen._api_get(action, {}))
            await pilot.pause()
            start = time.monotonic()
            await asyncio.sleep(0.2)
            elapsed = time.monotonic() - start
            assert elapsed < 1.0, f"loop blocked for {elapsed:.2f}s"
            result = await task
            assert result is not None

    _run(main())


def test_splash_escape_cancels_connection(mocker):
    """We expect escape on the splash to abort the connection attempt."""
    _patch_api(mocker)

    class SlowSchema:
        def __init__(self):
            self.release = threading.Event()

        @property
        def schema(self):
            self.release.wait(30)
            return {"paths": {}}

    slow = SlowSchema()
    mocker.patch("dokli.tui.app.APIClient", return_value=slow)

    async def main():
        app = DokliApp(config=_config(), connection=_connection())
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.pause()
            assert isinstance(app.screen, SplashScreen)
            await pilot.press("escape")
            await pilot.pause()
            assert not isinstance(app.screen, SplashScreen)
            await asyncio.sleep(1.5)
            await pilot.pause()
            assert not isinstance(app.screen, BrowserScreen)
            slow.release.set()

    _run(main())


def test_connection_reports_status_stages(mocker):
    """We expect the splash to report each preparation stage."""
    _patch_api(mocker)

    async def main():
        app = DokliApp(config=_config(), connection=_connection())
        spy = mocker.spy(app, "_splash_status")
        async with app.run_test() as pilot:
            await _wait_for_browser(app, pilot)
        texts = [call.args[0] for call in spy.call_args_list]
        assert "Fetching OpenAPI schema…" in texts
        assert "Parsing registry…" in texts
        assert "Preparing browser…" in texts

    _run(main())


def test_offline_connection_shows_error_and_loads_browser(mocker):
    """We expect no-connectivity (cached schema) to warn on the splash, load the
    browser from cache, and leave a toast."""
    _patch_api(mocker)
    registry = parse_spec(FAKE_SCHEMA)
    first_entity = next(iter(registry.listable()), None)

    def failing_request(method, path, params):
        if path == f"{first_entity}.all":
            raise httpx.ConnectError("down", request=httpx.Request("GET", "https://example.com/"))
        return FakeResponse({})

    import dokli.tui.app as tui_app

    tui_app.APIClient.return_value.request.side_effect = failing_request

    async def main():
        app = DokliApp(config=_config(), connection=_connection())
        notify = mocker.spy(app, "notify")
        async with app.run_test() as pilot:
            await pilot.pause()
            await _wait_for_browser(app, pilot)
            assert isinstance(app.screen, BrowserScreen)
        assert any("No connectivity" in str(call) for call in notify.call_args_list)

    _run(main())


def test_splash_spinner_animates(mocker):
    """We expect the splash spinner to cycle through frames over time."""
    _patch_api(mocker)

    async def main():
        app = DokliApp(config=_config())
        async with app.run_test() as pilot:
            splash = SplashScreen(classes="Splash")
            app.install_screen(splash, name="splash")
            app.push_screen("splash")
            await pilot.pause()
            label = splash.query_one("#splash-status", Label)
            first = str(label.renderable).split()[0]
            for _ in range(40):
                await pilot.pause()
                current = str(label.renderable).split()[0]
                if current != first:
                    break
            assert current != first
            assert current in SPINNER_FRAMES

    _run(main())


def test_browser_loading_indicator_toggles(mocker):
    """We expect the browser spinner to toggle on refresh."""
    _patch_api(mocker)
    registry = parse_spec(FAKE_SCHEMA)

    async def main():
        app = DokliApp(config=_config())
        async with app.run_test() as pilot:
            await _mount_browser(app, pilot, _connection(), registry)
            screen = app.screen
            loading = screen.query_one("#loading")
            assert loading.display is False
            screen._set_loading(True)
            await pilot.pause()
            assert loading.display is True
            screen._set_loading(False)
            await pilot.pause()
            assert loading.display is False

    _run(main())


def test_result_screen_loading_indicator(mocker):
    """We expect the result screen to host a togglable spinner."""
    _patch_api(mocker)
    registry = parse_spec(FAKE_SCHEMA)
    action = registry.get("project").get("all")

    async def main():
        app = DokliApp(config=_config())
        async with app.run_test() as pilot:
            screen = ResultScreen(_connection(), action, data={"items": []})
            app.install_screen(screen, name="result")
            app.push_screen("result")
            await pilot.pause()
            loading = screen.query_one("#result-loading")
            assert loading.display is False
            screen._set_loading(True)
            await pilot.pause()
            assert loading.display is True

    _run(main())


def test_auto_deploy_callback_gating(mocker):
    """We expect the auto-deploy hook to fire only when enabled and possible."""
    _patch_api(mocker)
    schema = {
        **FAKE_SCHEMA,
        "paths": {
            **FAKE_SCHEMA["paths"],
            "/compose.deploy": {
                "post": {
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {"composeId": {"type": "string"}},
                                    "required": ["composeId"],
                                }
                            }
                        }
                    }
                }
            },
        },
    }
    registry = parse_spec(schema)
    compose = registry.get("compose")
    update = compose.get("update")
    deploy = compose.get("deploy")
    assert deploy is not None

    def probe(auto_deploy: bool, action) -> BrowserScreen:
        config = Config(connections=[_connection()], tui=TuiConfig(auto_deploy=auto_deploy))
        app = DokliApp(config=config)

        async def main():
            async with app.run_test() as pilot:
                await _mount_browser(app, pilot, _connection(), registry)
                screen = app.screen
                level = screen.current
                level.kind = "compose"
                level.items = [{"_kind": "compose", "composeId": "c1", "name": "web"}]
                level.index = 0
                return screen._auto_deploy_callback(action)

        return _run(main())

    assert probe(False, update) is None
    assert probe(True, deploy) is None
    assert callable(probe(True, update))


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


def test_logs_merge_incremental_no_duplicates(mocker):
    """We expect follow-mode merges to append only newer lines."""
    _patch_api(mocker)
    registry = parse_spec(FAKE_SCHEMA)
    action = registry.get("compose").get("readLogs")

    screen = ResultScreen(_connection(), action, "", params={"composeId": "c1", "containerId": "cc1"})
    screen._lines = ["2026-08-05T19:55:54Z line a", "2026-08-05T19:55:55Z line b"]
    screen._merge_log_lines(["2026-08-05T19:55:55Z line b", "", "2026-08-05T19:56:00Z line c", ""])
    assert screen._lines == [
        "2026-08-05T19:55:54Z line a",
        "2026-08-05T19:55:55Z line b",
        "2026-08-05T19:56:00Z line c",
    ]
    screen._merge_log_lines(["2026-08-05T19:55:54Z line a", "2026-08-05T19:55:55Z line b", ""])
    assert screen._lines[-1] == "2026-08-05T19:56:00Z line c"
    assert len(screen._lines) == 3


def test_logs_follow_defaults_and_toggle(mocker):
    """We expect logs to follow by default and ``f`` to toggle it."""
    _patch_api(mocker)
    registry = parse_spec(FAKE_SCHEMA)
    logs_action = registry.get("compose").get("readLogs")
    plain_action = registry.get("project").get("all")

    logs_screen = ResultScreen(_connection(), logs_action, "")
    assert logs_screen._is_logs is True
    assert logs_screen._follow is True
    plain_screen = ResultScreen(_connection(), plain_action, "")
    assert plain_screen._is_logs is False
    assert plain_screen._follow is False

    async def main():
        app = DokliApp(config=_config())
        async with app.run_test() as pilot:
            screen = ResultScreen(
                _connection(),
                logs_action,
                "2026-08-05T19:55:54Z start",
                params={"composeId": "c1", "containerId": "cc1"},
            )
            app.install_screen(screen, name="result")
            app.push_screen("result")
            await pilot.pause()
            await pilot.pause()
            status = screen.query_one("#match-status", Label)
            assert "live" in str(status.renderable)
            assert screen._follow_worker is not None
            await pilot.press("f")
            await pilot.pause()
            assert screen._follow is False
            assert "follow off" in str(status.renderable)
            await pilot.press("f")
            await pilot.pause()
            assert screen._follow is True
            assert screen._follow_worker is not None

    _run(main())


def test_logs_timestamps_are_dimmed():
    """We expect docker log lines to render with their timestamp dimmed."""
    text = _log_line_text("2026-08-05T19:55:54Z frigate started")
    assert text.plain == "2026-08-05T19:55:54Z frigate started"
    assert text.spans and text.spans[0].style == "dim"
    assert text.plain.split()[-1] == "started"
    assert _timestamp_of("2026-08-05T19:55:54Z frigate started") is not None
    assert _timestamp_of("2026-08-05T19:55:54.123456Z x") is not None
    assert _timestamp_of("plain line") is None


def test_logs_fetch_follow_appends_and_pins(mocker):
    """We expect a follow poll to append newer lines and keep pinning the tail."""
    client = mocker.Mock()
    batches = iter(
        [
            FakeResponse("2026-08-05T19:55:55Z line 2\n2026-08-05T19:56:00Z line 3"),
        ]
    )
    client.request.side_effect = lambda method, path, params: next(batches)
    mocker.patch("dokli.tui.screens.generic.result.APIClient", return_value=client)
    registry = parse_spec(FAKE_SCHEMA)
    action = registry.get("compose").get("readLogs")

    async def main():
        app = DokliApp(config=_config())
        async with app.run_test() as pilot:
            screen = ResultScreen(
                _connection(),
                action,
                "2026-08-05T19:55:54Z line 1\n2026-08-05T19:55:55Z line 2",
                params={"composeId": "c1", "containerId": "cc1"},
            )
            app.install_screen(screen, name="result")
            app.push_screen("result")
            await pilot.pause()
            await pilot.pause()
            assert screen._lines[-1] == "2026-08-05T19:55:55Z line 2"
            await screen._fetch_follow()
            await pilot.pause()
            assert screen._lines[-1] == "2026-08-05T19:56:00Z line 3"
            assert screen._auto_scroll is True
            assert "live" in str(screen.query_one("#match-status", Label).renderable)

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
            related = await screen._related_records(screen.selected)
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


def test_related_containers_use_swarm_for_stacks(mocker):
    """We expect a stack-type compose to fetch containers from the swarm endpoint."""
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
                    items=[
                        {
                            "_kind": "compose",
                            "composeId": "c1",
                            "name": "stack",
                            "composeType": "stack",
                            "appName": "media-stack-abc123",
                            "serverId": "srv1",
                        }
                    ],
                    entity="compose",
                )
            ]
            screen.current.index = 0
            related = await screen._related_records(screen.selected)
            assert [r["name"] for r in related] == ["stack-svc"]
            calls = [c for c in screen.client.request.call_args_list if c[0][1].startswith("docker.get")]
            assert any(c[0][1] == "docker.getStackContainersByAppName" for c in calls)
            assert not any(c[0][1] == "docker.getContainersByAppNameMatch" for c in calls)

    _run(main())


def test_entity_list_uses_canonical_list_verb(mocker):
    """We expect deployment to be listed via its no-param allCentralized."""
    _patch_api(mocker)
    registry = parse_spec(FAKE_SCHEMA)

    async def main():
        app = DokliApp(config=_config())
        async with app.run_test() as pilot:
            await _mount_browser(app, pilot, _connection(), registry)
            _select(app, "deployment")
            await pilot.pause()
            await pilot.press("enter")
            await _wait_for_label(app, pilot, "media-torrents-abc123")
            screen = app.screen
            assert screen.current.kind == "deployment"
            calls = [c for c in screen.client.request.call_args_list if c[0][1] == "deployment.allCentralized"]
            assert calls

    _run(main())


def test_related_action_opens_deployments(mocker):
    """We expect a compose record to expose deployment.allByCompose as a
    separate action that opens a navigable deployment list."""
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
                    record={"composeId": "c1", "name": "torrents"},
                )
            ]
            screen.current.index = 0
            await pilot.pause()
            compose = registry.get("compose")
            bindings = {a.route: key for a, key in screen._entity_bindings(compose) if key}
            assert bindings["deployment.allByCompose"] == "d"
            contextual = dict(screen.contextual_bindings())
            assert any("deployment.allByCompose" in label for label in contextual.values())
            await pilot.press(bindings["deployment.allByCompose"])
            await _wait_for_label(app, pilot, "media-torrents-abc123")
            assert screen._selected_kind() == "deployment"
            deploy = registry.get("deployment")
            assert "deployment.readLogs" in {a.route for a, _ in screen._entity_bindings(deploy)}

    _run(main())



def test_drill_into_service_lists_containers_first(mocker):
    """We expect drilling into a service record to list containers before children."""
    _patch_api(mocker)
    registry = parse_spec(FAKE_SCHEMA)

    async def main():
        app = DokliApp(config=_config())
        async with app.run_test() as pilot:
            await _mount_browser(app, pilot, _connection(), registry)
            screen = app.screen
            screen.path = [
                Level(
                    kind="compose",
                    items=[{"_kind": "compose", "composeId": "c1", "name": "torrents"}],
                    entity="compose",
                )
            ]
            screen.current.index = 0
            await pilot.pause()
            await asyncio.sleep(0.2)
            await pilot.pause()
            await screen.action_right()
            await pilot.pause()
            assert screen.current.kind == "categories"
            assert {"Containers", "Deployments", "Domain", "Mount"} <= {item["label"] for item in screen.current.items}
            containers_idx = next(
                i for i, item in enumerate(screen.current.items) if item.get("_category") == "containers"
            )
            screen.current.index = containers_idx
            await pilot.pause()
            await screen.action_right()
            await pilot.pause()
            items = screen.current.items
            assert items and items[0]["_kind"] == "docker"
            kinds = [item["_kind"] for item in items]
            assert "docker" in kinds
            docker = registry.get("docker")
            assert "docker.restartContainer" in {a.route for a, _ in screen._entity_bindings(docker)}

    _run(main())


def test_container_contextual_logs(mocker):
    """We expect a docker container to expose the parent service's readLogs."""
    _patch_api(mocker)
    registry = parse_spec(FAKE_SCHEMA)

    async def main():
        app = DokliApp(config=_config())
        async with app.run_test() as pilot:
            await _mount_browser(app, pilot, _connection(), registry)
            screen = app.screen
            screen.path = [
                Level(
                    kind="compose",
                    items=[{"_kind": "compose", "composeId": "c1", "name": "torrents"}],
                    entity="compose",
                )
            ]
            screen.current.index = 0
            await pilot.pause()
            await asyncio.sleep(0.2)
            await pilot.pause()
            await screen.action_right()
            await pilot.pause()
            containers_idx = next(
                i for i, item in enumerate(screen.current.items) if item.get("_category") == "containers"
            )
            screen.current.index = containers_idx
            await pilot.pause()
            await screen.action_right()
            await pilot.pause()
            screen.current.index = 0
            await pilot.pause()
            docker = registry.get("docker")
            bindings = {a.route: key for a, key in screen._entity_bindings(docker) if key}
            assert bindings["compose.readLogs"] == "L"
            await pilot.press(bindings["compose.readLogs"])
            await pilot.pause()
            calls = [c for c in screen.client.request.call_args_list if c[0][1] == "compose.readLogs"]
            assert calls
            params = calls[-1][0][2]
            assert params.get("containerId") == "cc1"
            assert params.get("composeId") == "c1"

    _run(main())


def test_record_categories_counts(mocker):
    """We expect nested child arrays to carry free counts and lazy ones not."""
    _patch_api(mocker)
    registry = parse_spec(FAKE_SCHEMA)

    async def main():
        app = DokliApp(config=_config())
        async with app.run_test() as pilot:
            await _mount_browser(app, pilot, _connection(), registry)
            screen = app.screen
            record = {
                "_kind": "compose",
                "composeId": "c1",
                "name": "torrents",
                "domains": [{"domainId": "d1"}, {"domainId": "d2"}],
                "mounts": [{"mountId": "m1"}],
            }
            screen.path = [Level(kind="compose", items=[record], entity="compose")]
            screen.current.index = 0
            await pilot.pause()
            cats = {category["label"]: category for category in screen._record_categories(record)}
            assert cats["Containers"]["count"] is None
            assert cats["Deployments"]["count"] is None
            assert cats["Domain"]["count"] == 2
            assert cats["Mount"]["count"] == 1

    _run(main())


def test_mount_title_uses_path():
    """We expect mounts to be titled by their host file path, not their id."""
    from dokli.tui.engine import record_title

    assert record_title({"mountId": "m1", "mountPath": "/", "filePath": "/srv/data"}) == "/srv/data"
    assert record_title({"mountId": "m2", "mountPath": "/", "volumeName": "myvol"}) == "myvol"


def test_create_form_prefills_parent(mocker):
    """We expect a create form opened from a service category to hide parent-id
    fields and prefill derived ones."""
    _patch_api(mocker)
    registry = parse_spec(FAKE_SCHEMA)

    async def main():
        app = DokliApp(config=_config())
        async with app.run_test() as pilot:
            await _mount_browser(app, pilot, _connection(), registry)
            screen = app.screen
            screen.path = [
                Level(
                    kind="domain",
                    items=[],
                    entity="compose",
                    record={"composeId": "c1", "name": "torrents"},
                )
            ]
            await pilot.pause()
            domain = registry.get("domain")
            await screen._open_form(domain.get("create"))
            await pilot.pause()
            form_screen = app.screen
            assert isinstance(form_screen, ActionFormScreen)
            assert "composeId" not in form_screen.form.fields
            assert "applicationId" not in form_screen.form.fields
            assert form_screen.inject == {"composeId": "c1"}
            assert str(form_screen.form.fields["domainType"].value) == "compose"

    _run(main())


def test_create_form_injects_parent_on_submit(mocker):
    """We expect the hidden parent id to be sent on submit."""
    _patch_api(mocker)
    registry = parse_spec(FAKE_SCHEMA)

    async def main():
        app = DokliApp(config=_config())
        async with app.run_test() as pilot:
            await _mount_browser(app, pilot, _connection(), registry)
            screen = app.screen
            screen.path = [
                Level(
                    kind="domain",
                    items=[],
                    entity="compose",
                    record={"composeId": "c1", "name": "torrents"},
                )
            ]
            await pilot.pause()
            domain = registry.get("domain")
            await screen._open_form(domain.get("create"))
            await pilot.pause()
            form_screen = app.screen
            form_screen.form.fields["host"].value = "x.example.com"
            form_screen.action_submit()
            await pilot.pause()
            await pilot.press("y")
            await asyncio.sleep(0.2)
            await pilot.pause()
            await pilot.pause()
            calls = [c for c in screen.client.request.call_args_list if c[0][1] == "domain.create"]
            assert calls
            body = calls[-1][0][2].get("body", {})
            assert body.get("composeId") == "c1"
            assert body.get("host") == "x.example.com"

    _run(main())


def test_form_parent_ids_visible_without_context():
    """We expect parent-id fields to stay editable when there is no parent context."""
    from dokli.tui.engine.schemas import build_form_model

    schema = {
        "type": "object",
        "properties": {
            "host": {"type": "string"},
            "composeId": {"type": "string"},
            "applicationId": {"type": "string"},
        },
    }
    model = build_form_model(schema)
    assert "composeId" in model.model_fields
    assert "applicationId" in model.model_fields


def test_empty_child_category_allows_create(mocker):
    """We expect an empty nested array to still yield a category so the first
    child record can be created (e.g. a compose with no domains yet)."""
    _patch_api(mocker)
    registry = parse_spec(FAKE_SCHEMA)

    async def main():
        app = DokliApp(config=_config())
        async with app.run_test() as pilot:
            await _mount_browser(app, pilot, _connection(), registry)
            screen = app.screen
            record = {"_kind": "compose", "composeId": "c1", "name": "torrents", "domains": []}
            screen.path = [Level(kind="compose", items=[record], entity="compose")]
            screen.current.index = 0
            await pilot.pause()
            cats = {category["label"]: category for category in screen._record_categories(record)}
            assert cats["Domain"]["count"] == 0
            await screen._open_category(cats["Domain"], record)
            await pilot.pause()
            assert screen.current.kind == "domain"
            assert screen.current.items == []
            domain = registry.get("domain")
            assert any(a.route == "domain.create" for a, _ in screen._entity_bindings(domain))

    _run(main())


def test_category_picker_uses_child_entity(mocker):
    """We expect selecting a category to expose that child entity's actions
    (e.g. 'create domain'), not the parent service's."""
    _patch_api(mocker)
    registry = parse_spec(FAKE_SCHEMA)

    async def main():
        app = DokliApp(config=_config())
        async with app.run_test() as pilot:
            await _mount_browser(app, pilot, _connection(), registry)
            screen = app.screen
            record = {"_kind": "compose", "composeId": "c1", "name": "torrents", "domains": []}
            screen.path = [Level(kind="compose", items=[record], entity="compose")]
            screen.current.index = 0
            await pilot.pause()
            await screen.action_right()
            await pilot.pause()
            assert screen.current.kind == "categories"
            domain_idx = next(i for i, item in enumerate(screen.current.items) if item.get("child_entity") == "domain")
            screen.current.index = domain_idx
            await pilot.pause()
            assert screen._selected_kind() == "domain"
            domain = registry.get("domain")
            assert any(a.route == "domain.create" for a, _ in screen._entity_bindings(domain))

    _run(main())


def test_service_update_form_keeps_fk_fields(mocker):
    """We expect service entities' own update forms to keep FK fields editable
    (environmentId, githubId) even with a parent context."""
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
                    items=[{"_kind": "application", "applicationId": "a1", "name": "web"}],
                    entity="application",
                    record={"applicationId": "a1", "name": "web"},
                )
            ]
            screen.current.index = 0
            await pilot.pause()
            entity = registry.get("application")
            await screen._open_form(entity.get("update"))
            await pilot.pause()
            form_screen = app.screen
            assert isinstance(form_screen, ActionFormScreen)
            assert "environmentId" in form_screen.form.fields
            assert "githubId" in form_screen.form.fields
            assert "applicationId" not in form_screen.form.fields
            assert form_screen.inject == {"applicationId": "a1"}

    _run(main())


def test_child_update_form_hides_own_and_parent_ids(mocker):
    """We expect a child update form to hide its own primary key and the parent
    id, injecting both from the record."""
    _patch_api(mocker)
    registry = parse_spec(FAKE_SCHEMA)

    async def main():
        app = DokliApp(config=_config())
        async with app.run_test() as pilot:
            await _mount_browser(app, pilot, _connection(), registry)
            screen = app.screen
            screen.path = [
                Level(
                    kind="domain",
                    items=[
                        {
                            "_kind": "domain",
                            "domainId": "d1",
                            "host": "x.example.com",
                            "composeId": "c1",
                        }
                    ],
                    entity="compose",
                    record={"composeId": "c1", "name": "torrents"},
                )
            ]
            screen.current.index = 0
            await pilot.pause()
            domain = registry.get("domain")
            await screen._open_form(domain.get("update"))
            await pilot.pause()
            form_screen = app.screen
            assert isinstance(form_screen, ActionFormScreen)
            assert "domainId" not in form_screen.form.fields
            assert "composeId" not in form_screen.form.fields
            assert form_screen.inject == {"domainId": "d1", "composeId": "c1"}

    _run(main())


def test_result_refresh_keeps_single_label(mocker):
    """We expect re-rendering the result to update a single persistent label
    (no remove/mount churn that would destabilize the scrollbar)."""
    _patch_api(mocker)
    registry = parse_spec(FAKE_SCHEMA)
    action = registry.get("compose").get("readLogs")

    async def main():
        app = DokliApp(config=_config())
        async with app.run_test() as pilot:
            screen = ResultScreen(_connection(), action, data="line1\nline2", params={})
            app.install_screen(screen, name="result")
            app.push_screen("result")
            await pilot.pause()
            screen._query = "line"
            await screen._apply_search()
            await pilot.pause()
            container = screen.query_one("#result-scroll", VerticalScroll)
            assert len(container.children) == 1
            assert "line1" in str(screen.query_one("#result", Label).renderable)
            screen._query = ""
            await screen._apply_search()
            await pilot.pause()
            assert len(screen.query_one("#result-scroll", VerticalScroll).children) == 1

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
            await _wait_for_browser(app, pilot)
            assert isinstance(app.screen, BrowserScreen)

    _run(main())


def test_connection_argument_opens_browser_directly(mocker):
    """We expect DokliApp(connection=...) to open the browser directly on mount."""
    _patch_api(mocker)

    async def main():
        app = DokliApp(config=_config(), connection=_connection())
        async with app.run_test() as pilot:
            await _wait_for_browser(app, pilot)
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


def test_save_connection_with_keyring_stores_key(mocker, fake_keyring):
    """We expect saving a connection with the keychain toggle to store the key there."""
    config = _config()
    save = mocker.patch("dokli.config.Config.save")
    connection = ConnectionConfig(name="stage", url="https://stage.example.com", api_key="*" * 64, api_key_keyring=True)

    async def main():
        app = DokliApp(config=config)
        async with app.run_test() as pilot:
            await pilot.pause()
            app.on_connections_screen_add_connection(ConnectionsScreen.AddConnection(connection=connection))
            assert fake_keyring.store[("dokli", "conn.stage")] == "*" * 64
            saved = next(c for c in app.config.connections if c.name == "stage")
            assert saved.api_key is None
            assert saved.api_key_keyring is True
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


def test_switch_connection_reuses_browser(mocker):
    """We expect switching connections to reload the browser, not re-install it."""
    _patch_api(mocker)

    async def main():
        app = DokliApp(config=_config(), connection=_connection())
        async with app.run_test() as pilot:
            await _wait_for_browser(app, pilot)
            first = app.screen
            # go back to the connections screen and pick another connection
            app.action_connections()
            for _ in range(10):
                await pilot.pause()
                if isinstance(app.screen, ConnectionsScreen):
                    break
            assert isinstance(app.screen, ConnectionsScreen)
            second = ConnectionConfig(name="stage", url="https://stage.example.com", api_key_cmd="echo key")
            app.set_connection(second)
            await _wait_for_browser(app, pilot)
            assert isinstance(app.screen, BrowserScreen)
            assert app.screen is first
            assert app.screen.connection.name == "stage"

    _run(main())


# -- help + command palette -------------------------------------------------


def test_help_screen_shows_bindings(mocker):
    """We expect ? to open the help screen listing the keybindings."""
    _patch_api(mocker)

    async def main():
        app = DokliApp(config=_config(), connection=_connection())
        async with app.run_test() as pilot:
            await _wait_for_browser(app, pilot)
            # select 'project' so its contextual actions are available
            screen = app.screen
            vis = screen._visible_items(screen.current)
            screen.current.index = next(i for i, item in enumerate(vis) if item.get("name") == "project")
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
