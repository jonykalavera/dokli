"""Dokli TUI."""

from collections.abc import Callable
from functools import partial
from pathlib import Path
from typing import Any, cast

import httpx
from textual import events, log
from textual.app import App, ComposeResult, get_system_commands
from textual.command import DiscoveryHit, Hit, Hits, Provider
from textual.design import ColorSystem
from textual.widgets import Footer, Header, Static

from dokli.api_client import APIClient
from dokli.config import Config, ConnectionConfig
from dokli.tui.engine import parse_spec, record_title
from dokli.tui.screens.connections import ConnectionsScreen
from dokli.tui.screens.generic.browser import BrowserScreen
from dokli.tui.screens.generic.form import ActionFormScreen
from dokli.tui.screens.generic.help import HelpScreen
from dokli.tui.screens.settings import SettingsScreen

TUI_PATH = Path(__file__).parent
ASCII_ART_PATH = TUI_PATH / "asciiart"


def _catppuccin_design() -> dict[str, ColorSystem]:
    """A Catppuccin (Mocha/Latte) color system for the app."""
    return {
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


class DokliCommands(Provider):
    """Commands for the Dokli command palette (context-aware)."""

    # Core commands that have an app-level keybinding shown in the help line.
    _CORE_KEYS = {
        "Toggle dark mode": "d",
        "Connections": "C",
        "Help": "?",
        "Quit": "q",
    }

    def _commands(self) -> list[tuple[str, str, Callable[[], Any]]]:
        app = cast(DokliApp, self.app)
        commands = [
            ("Toggle dark mode", "Switch between light and dark themes", app.action_toggle_dark),
            ("Connections", "Open the connections screen", app.action_connections),
            ("Settings", "Open the settings screen", app.action_settings),
            ("Help", "Show the keybindings", app.action_help),
            ("Quit", "Exit the app", app.action_quit),
        ]
        commands = [
            (name, _with_key(help_text, self._CORE_KEYS.get(name)), callback)
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
        ("d", "toggle_dark", "Toggle dark mode"),
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
        self.design = _catppuccin_design()
        self.config = config or Config()
        self.connection: ConnectionConfig | None = connection

    def on_mount(self) -> None:
        """On mount."""
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
        try:
            schema = APIClient(connection).schema
        except httpx.HTTPError as err:
            self._connection_failed(connection, err)
            return
        registry = parse_spec(schema)
        self.install_screen(
            BrowserScreen(name="Browser", connection=self.connection, registry=registry),
            name="Browser",
        )
        self.push_screen("Browser")

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
        self.notify(f"Added connection '{event.connection.name}'.")

    def on_connections_screen_update_connection(self, event: ConnectionsScreen.UpdateConnection) -> None:
        """Persist an edited connection."""
        self._save_connection(event.connection)
        self.notify(f"Updated connection '{event.connection.name}'.")

    def on_connections_screen_delete_connection(self, event: ConnectionsScreen.DeleteConnection) -> None:
        """Persist a deleted connection."""
        self.config.connections = [
            connection for connection in self.config.connections if connection.name != event.connection.name
        ]
        self.config.save()
        self.notify(f"Deleted connection '{event.connection.name}'.")

    def _save_connection(self, connection: ConnectionConfig) -> None:
        """Add or update a connection in the config and persist it."""
        names = [existing.name for existing in self.config.connections]
        if connection.name in names:
            self.config.connections = [
                connection if existing.name == connection.name else existing for existing in self.config.connections
            ]
        else:
            self.config.connections = [*self.config.connections, connection]
        self.config.save()

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
