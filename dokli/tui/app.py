"""Dokli TUI."""

import asyncio
from collections.abc import Callable
from functools import partial
from pathlib import Path
from typing import Any, cast

import httpx
from textual import events, log
from textual.app import App, ComposeResult, get_system_commands
from textual.binding import _Bindings
from textual.command import DiscoveryHit, Hit, Hits, Provider
from textual.design import ColorSystem
from textual.widgets import Footer, Header, Static
from textual.worker import get_current_worker

from dokli.api_client import APIClient
from dokli.config import Config, ConnectionConfig
from dokli.secrets import conn_account, set_secret
from dokli.tui.engine import parse_spec, record_title
from dokli.tui.engine.icons import set_entity_color_overrides, set_state_color_overrides
from dokli.tui.screens.connections import ConnectionsScreen
from dokli.tui.screens.generic.browser import BrowserScreen
from dokli.tui.screens.generic.form import ActionFormScreen
from dokli.tui.screens.generic.help import HelpScreen
from dokli.tui.screens.settings import SettingsScreen
from dokli.tui.screens.splash import SplashScreen

TUI_PATH = Path(__file__).parent
ASCII_ART_PATH = TUI_PATH / "asciiart"

# Cap on the schema fetch, so a hanging DNS/connect cannot freeze the splash.
SCHEMA_FETCH_TIMEOUT = 15.0

# Cap on the live connectivity check performed after a cached schema load.
CONNECTIVITY_TIMEOUT = 5.0


def _build_connection_client(connection: ConnectionConfig) -> tuple[APIClient, dict]:
    """Build an API client (fetching the schema) in a worker thread."""
    client = APIClient(connection)
    return client, client.schema

# App-level action -> (default key, help text). Remappable via tui.keys.app.
APP_ACTIONS: dict[str, tuple[str, str]] = {
    "toggle_dark": ("D", "Toggle dark mode"),
    "connections": ("C", "Connections"),
    "help": ("?", "Help"),
    "command_palette": ("ctrl+p", "Command palette"),
    "cancel": ("escape", "Cancel/Back"),
    "quit": ("q", "Quit"),
}

# Color fields that define the theme's structure: they follow the active
# variant (so toggling light/dark still switches the background).
TUI_STRUCTURAL = frozenset({"background", "surface", "panel"})


def _catppuccin_design(overrides: dict[str, str] | None = None, dark: bool = True) -> dict[str, ColorSystem]:
    """A Catppuccin (Mocha/Latte) color system for the app.

    ``overrides`` are color fields. Accent fields (primary, secondary, accent,
    warning, error, success, boost) apply to both variants; structural fields
    (background, surface, panel) apply only to the active ``dark`` variant so
    the light/dark toggle stays meaningful.
    """
    overrides = overrides or {}
    accents = {key: value for key, value in overrides.items() if key not in TUI_STRUCTURAL}
    structural = {key: value for key, value in overrides.items() if key in TUI_STRUCTURAL}
    variants = {
        "dark": ColorSystem(
            primary="#cba6f7",
            secondary="#f5c2e7",
            warning="#f9e2af",
            error="#f38ba8",
            success="#a6e3a1",
            accent="#89b4fa",
            background="#1e1e2e",
            surface="#313244",
            dark=True,
        ),
        "light": ColorSystem(
            primary="#8839ef",
            secondary="#ea76cb",
            warning="#df8e1d",
            error="#d20f39",
            success="#40a02b",
            accent="#1e66f5",
            background="#eff1f5",
            surface="#ccd0da",
            dark=False,
        ),
    }
    return {
        name: _with_color_overrides(variant, {**accents, **(structural if (name == "dark") == dark else {})})
        for name, variant in variants.items()
    }


def _with_color_overrides(base: ColorSystem, overrides: dict[str, str]) -> ColorSystem:
    """Rebuild a ColorSystem with the given field overrides applied."""
    if not overrides:
        return base
    kwargs = {
        "primary": base.primary,
        "secondary": base.secondary,
        "warning": base.warning,
        "error": base.error,
        "success": base.success,
        "accent": base.accent,
        "background": base.background,
        "surface": base.surface,
        "panel": base.panel,
        "boost": base.boost,
        "dark": getattr(base, "dark", False),
    }
    kwargs.update({key: value for key, value in overrides.items() if key in kwargs and value is not None})
    return ColorSystem(**kwargs)  # ty: ignore[invalid-argument-type]


class DokliCommands(Provider):
    """Commands for the Dokli command palette (context-aware)."""

    # Core commands that have an app-level keybinding shown in the help line.
    _CORE_KEY_ACTIONS = {
        "Toggle dark mode": "toggle_dark",
        "Connections": "connections",
        "Help": "help",
        "Quit": "quit",
    }

    def _core_keys(self) -> dict[str, str | None]:
        """The effective keys for the core palette commands."""
        app = cast(DokliApp, self.app)
        return {
            name: app.app_keys.get(action) for name, action in self._CORE_KEY_ACTIONS.items()
        }

    def _commands(self) -> list[tuple[str, str, Callable[[], Any]]]:
        app = cast(DokliApp, self.app)
        commands: list[tuple[str, str, Callable[[], Any]]] = [
            ("Toggle dark mode", "Switch between light and dark themes", app.action_toggle_dark),
            ("Connections", "Open the connections screen", app.action_connections),
            ("Settings", "Open the settings screen", app.action_settings),
            ("Help", "Show the keybindings", app.action_help),
            ("Quit", "Exit the app", app.action_quit),
        ]
        commands = [
            (name, _with_key(help_text, self._core_keys().get(name)), callback)
            for name, help_text, callback in commands
        ]
        commands.extend(_screen_commands(self.screen))
        for connection in app.config.connections:
            commands.append(
                (
                    f"Open {connection.name}",
                    f"Open the browser on the {connection.name} connection",
                    partial(app.set_connection, connection),
                )
            )
        return commands

    async def search(self, query: str) -> Hits:
        """Search commands by name."""
        query = query.lower()
        for name, help_text, callback in self._commands():
            if query in name.lower():
                yield Hit(1.0, name, callback, name, help_text)

    async def discover(self) -> Hits:
        """Show all commands when the palette is opened empty."""
        for name, help_text, callback in self._commands():
            yield DiscoveryHit(name, callback, name, help_text)


def _screen_commands(screen) -> list[tuple[str, str, Callable[[], Any]]]:
    """Context-aware commands for the screen that opened the palette."""
    commands: list[tuple[str, str, Callable[[], Any]]] = []
    if isinstance(screen, BrowserScreen):
        commands.extend(_browser_commands(screen))
    elif isinstance(screen, ActionFormScreen):
        commands.extend(
            [
                ("Submit form", "Validate and run the form action", screen.action_submit),
                ("Wizard mode", "Step through the fields one at a time", screen.action_wizard),
                ("Cancel", "Close the form without running", screen.action_cancel),
            ]
        )
    elif isinstance(screen, ConnectionsScreen):
        commands.extend(
            [
                ("Add connection", "Create a new connection", screen.action_add_connection),
                ("Edit connection", "Edit the highlighted connection", screen.action_edit_connection),
            ]
        )
    return commands


def _with_key(help_text: str, key: str | None) -> str:
    """Prepend a shortcut to a command's help line when it has one."""
    return f"[{key}] {help_text}" if key else help_text


def _browser_commands(screen: BrowserScreen) -> list[tuple[str, str, Callable[[], Any]]]:
    """Commands for the browser: the selected entity's available actions."""
    commands: list[tuple[str, str, Callable[[], Any]]] = []
    kind = screen._selected_kind()
    entity = screen.registry.get(kind or "")
    if entity is None:
        return commands
    selected = screen.selected or {}
    title = record_title(selected) if selected else (kind or "record")
    for action, key in screen._entity_bindings(entity):
        help_text = _with_key(f"{action.verb} · {kind} ({action.method})", key)
        commands.append(
            (
                f"Run {action.verb} on {title}",
                help_text,
                partial(screen._run_action, action),
            )
        )
    return commands


class DokliApp(App):
    """A Textual app to manage stopwatches."""

    TITLE = "Dokli"
    CSS_PATH = "css/tui.css"
    COMMANDS = {get_system_commands, DokliCommands}
    BINDINGS = [
        ("D", "toggle_dark", "Toggle dark mode"),
        ("C", "connections", "Connections"),
        ("?", "help", "Help"),
        ("ctrl+p", "command_palette", "Command palette"),
        ("escape", "cancel", "Cancel/Back"),
        ("q", "quit", "Quit"),
    ]

    config: Config
    connection: ConnectionConfig | None

    def __init__(
        self,
        config: Config | None = None,
        connection: ConnectionConfig | None = None,
        **kwargs,
    ) -> None:
        """Construct a new TUI app."""
        super().__init__(**kwargs)
        self.config = config or Config()
        self.connection: ConnectionConfig | None = connection
        self.design = _catppuccin_design(self.config.tui.colors or None, self.config.tui.dark)
        set_entity_color_overrides(self.config.tui.entity_colors)
        set_state_color_overrides(self.config.tui.state_colors)
        self.dark = self.config.tui.dark
        self.app_keys = {
            action: (self.config.tui.keys.app or {}).get(action, default)
            for action, (default, _) in APP_ACTIONS.items()
        }
        # Replace the class-level bindings with the config-derived ones so the
        # Footer/help reflect any remapped app keys.
        self._bindings = _Bindings(
            [
                (self.app_keys[action], action, help_text)
                for action, (_, help_text) in APP_ACTIONS.items()
            ]
        )

    def tui_keybindings(self) -> dict:
        """Keybinding overrides for the entity registry (verb keys, reserved keys)."""
        return {
            "verb_keys": self.config.tui.keys.verbs or None,
            "system_keys": frozenset(
                key for key in self.app_keys.values() if len(key) == 1 and key.isalnum()
            ),
        }

    def on_mount(self) -> None:
        """On mount."""
        # The stylesheet is built in App.__init__ with the default design; when
        # the configured theme equals the default, no dark-change event fires,
        # so force a refresh to apply the custom design at startup.
        self.call_later(self.refresh_css)
        self.install_screen(ConnectionsScreen(self.config.connections), name="Connections")
        self.install_screen(SettingsScreen(name="Settings"), name="Settings")

        if self.connection:
            self.set_connection(self.connection)
        else:
            self.push_screen("Connections")

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark

    def action_cancel(self) -> None:
        """Cancel action."""
        if len(self.screen_stack) > 1:
            self.pop_screen()
        else:
            self.bell()

    def action_help(self) -> None:
        """Open the help screen."""
        self.push_screen(HelpScreen(classes="Help"))

    def action_settings(self) -> None:
        """Open the settings screen."""
        self.push_screen("Settings")

    def set_connection(self, connection: ConnectionConfig) -> None:
        """Set the active connection and open the entity browser."""
        self.connection = connection
        log.info(f"Setting connection: {connection}")
        self._splash = SplashScreen(classes="Splash")
        self.push_screen(self._splash)
        self._connection_worker = self.run_worker(
            self._prepare_connection(connection), exclusive=True, group="connection"
        )

    async def _prepare_connection(self, connection: ConnectionConfig) -> None:
        """Fetch the schema and build the browser entirely off the event loop."""
        try:
            self._splash_status("Fetching OpenAPI schema…")
            # Fetch the schema AND build the API client in a worker thread so no
            # network call ever runs on the event loop (an unreachable host would
            # otherwise freeze the whole UI until the network returns).
            client, schema = await asyncio.wait_for(
                asyncio.to_thread(_build_connection_client, connection),
                timeout=SCHEMA_FETCH_TIMEOUT,
            )
            self._splash_status("Parsing registry…")
            registry = parse_spec(schema)
            self._splash_status("Checking connectivity…")
            online = await self._check_connectivity(client, registry)
            self._splash_status("Preparing browser…")
            browser = self._installed_screens.get("Browser")
            if isinstance(browser, BrowserScreen):
                browser.reload(connection, registry, entity_order=self.config.tui.entity_order, client=client)
            else:
                browser = BrowserScreen(
                    name="Browser",
                    connection=connection,
                    registry=registry,
                    entity_order=self.config.tui.entity_order,
                    client=client,
                )
                self.install_screen(browser, name="Browser")
        except (httpx.HTTPError, asyncio.TimeoutError) as err:
            self._pop_splash()
            self._connection_failed(connection, err)
            return
        except Exception:
            self._pop_splash()
            self._connection_failed(connection, RuntimeError("Could not prepare the connection."))
            return
        if not online:
            self._splash_error(connection)
            # Hold briefly so the error is visible on the splash before the
            # browser (loaded from cache) takes over.
            await asyncio.sleep(0.8)
        self._pop_splash()
        if browser in self.screen_stack:
            while self.screen_stack and self.screen_stack[-1] is not browser:
                self.pop_screen()
        else:
            self.push_screen("Browser")
        if not online:
            self.notify(f"No connectivity to {connection.name} — actions may fail.", severity="error", timeout=8)

    async def _check_connectivity(self, client: APIClient, registry) -> bool:
        """Return whether the instance is actually reachable (not just cached)."""
        entity = next(iter(registry.listable()), None)
        if entity is None:
            return True
        try:
            await asyncio.wait_for(
                asyncio.to_thread(client.request, "GET", f"{entity}.all", {}),
                timeout=CONNECTIVITY_TIMEOUT,
            )
            return True
        except (httpx.TransportError, asyncio.TimeoutError):
            return False
        except httpx.HTTPStatusError:
            # The API responded (even with an error) — connectivity exists.
            return True

    def _splash_error(self, connection: ConnectionConfig) -> None:
        """Mark the splash status as an error (shown on the way to the browser)."""
        splash = getattr(self, "_splash", None)
        if splash is not None:
            splash.set_status(f"No connectivity to {connection.name} — actions may fail.", error=True)

    def _splash_status(self, text: str) -> None:
        """Update the splash status line (stored even before the splash mounts)."""
        splash = getattr(self, "_splash", None)
        if splash is not None:
            splash.set_status(text)

    def _pop_splash(self) -> None:
        """Pop the splash screen (if showing) and cancel its connection worker."""
        splash = getattr(self, "_splash", None)
        if splash is not None and splash in self.screen_stack:
            self.pop_screen()
        self._splash = None
        worker = getattr(self, "_connection_worker", None)
        try:
            current = get_current_worker()
        except Exception:
            current = None
        if worker is not None and worker is not current:
            worker.cancel()
        self._connection_worker = None

    def cancel_connection(self) -> None:
        """Abort an in-flight connection attempt and return to the previous screen."""
        self._pop_splash()

    def _connection_failed(self, connection: ConnectionConfig, err: Exception) -> None:
        """Fall back to the connections screen when a connection is unreachable."""
        self.push_screen("Connections")
        self.notify(f"Could not reach {connection.name}: {err}", severity="error", timeout=10)

    def on_connections_screen_set_connection(self, event: ConnectionsScreen.SetConnection) -> None:
        """Handle connection set screen event."""
        self.set_connection(event.connection)

    def on_connections_screen_add_connection(self, event: ConnectionsScreen.AddConnection) -> None:
        """Persist a newly added connection."""
        self._save_connection(event.connection)
        self._sync_connections_list()
        self.notify(f"Added connection '{event.connection.name}'.")

    def on_connections_screen_update_connection(self, event: ConnectionsScreen.UpdateConnection) -> None:
        """Persist an edited connection."""
        self._save_connection(event.connection, original=event.original)
        self._sync_connections_list()
        self.notify(f"Updated connection '{event.connection.name}'.")

    def on_connections_screen_delete_connection(self, event: ConnectionsScreen.DeleteConnection) -> None:
        """Persist a deleted connection."""
        self.config.connections = [
            connection for connection in self.config.connections if connection.name != event.connection.name
        ]
        self.config.save()
        self._sync_connections_list()
        self.notify(f"Deleted connection '{event.connection.name}'.")

    def _save_connection(self, connection: ConnectionConfig, original: ConnectionConfig | None = None) -> None:
        """Add or update a connection in the config and persist it.

        When ``original`` is given (edit with a possible rename), the entry is
        replaced by the original's identity so a rename does not duplicate it.
        """
        if connection.api_key_keyring and connection.api_key is not None:
            set_secret(conn_account(connection.name), connection.api_key.get_secret_value())
            connection = connection.model_copy(update={"api_key": None})
        names = [existing.name for existing in self.config.connections]
        if original is not None and original.name in names:
            target = original.name
        elif connection.name in names:
            target = connection.name
        else:
            self.config.connections = [*self.config.connections, connection]
            self.config.save()
            return
        self.config.connections = [
            connection if existing.name == target else existing for existing in self.config.connections
        ]
        self.config.save()

    def _sync_connections_list(self) -> None:
        """Refresh the connections screen list from the persisted config."""
        if self.screen_stack and isinstance(self.screen_stack[-1], ConnectionsScreen):
            self.screen_stack[-1].connections = list(self.config.connections)

    def action_connections(self) -> None:
        """Action connections."""
        if self.screen.name != "Connections":
            self.push_screen("Connections")

    def compose(self) -> "ComposeResult":
        """Compose the widget."""
        yield Header()
        yield Footer()
        with open(ASCII_ART_PATH / "dokploy-logo-notext.txt") as logo:
            yield Static("".join(logo.readlines()), id="logo")

    def on_screen_resume(self, event: events.ScreenResume) -> None:
        """On screen resume."""
        self.app.sub_title = ""


app = DokliApp()
