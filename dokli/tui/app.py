"""Dokli TUI."""

from pathlib import Path

import httpx
from textual import events, log
from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Static

from dokli.api_client import APIClient
from dokli.config import Config, ConnectionConfig
from dokli.tui.engine import parse_spec
from dokli.tui.screens.connections import ConnectionsScreen
from dokli.tui.screens.generic.browser import BrowserScreen
from dokli.tui.screens.settings import SettingsScreen

TUI_PATH = Path(__file__).parent
ASCII_ART_PATH = TUI_PATH / "asciiart"


class DokliApp(App):
    """A Textual app to manage stopwatches."""

    TITLE = "Dokli"
    CSS_PATH = "css/tui.css"
    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("C", "connections", "Connections"),
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

    def action_connections(self) -> None:
        """Action connections."""
        if self.connection:
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
