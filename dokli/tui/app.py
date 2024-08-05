"""Dokli TUI."""

from pathlib import Path

from textual import events, log
from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Static

from dokli.config import Config, ConnectionConfig
from dokli.tui.screens.connections import ConnectionsScreen
from dokli.tui.screens.projects import ProjectsScreen
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
    connection: ConnectionConfig

    def __init__(self, config: Config | None = None, **kwargs) -> None:
        """Construct a new TUI app."""
        super().__init__(**kwargs)
        self.config = config or Config()
        self.connection: ConnectionConfig | None = None

    def on_mount(self) -> None:
        """On mount."""
        self.install_screen(ConnectionsScreen(self.config.connections), name="Connections")
        self.install_screen(ProjectsScreen(name="Projects"), name="Projects")
        self.install_screen(SettingsScreen(name="Settings"), name="Settings")
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

    def on_connections_screen_set_connection(self, event: ConnectionsScreen.SetConnection) -> None:
        """Set the active connection."""
        self.connection = event.connection
        log.info(f"Setting connection: {event.connection}")
        self.push_screen("Projects")

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
        self.app.sub_title = None


app = DokliApp()
