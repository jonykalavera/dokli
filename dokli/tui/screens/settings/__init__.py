"""Settings screen."""

from typing import TYPE_CHECKING

from textual import events
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Footer, Header, Label

from dokli.config import ConnectionConfig
from dokli.tui.widgets.main_menu import MainMenu

if TYPE_CHECKING:
    from textual.app import ComposeResult


class SettingsScreen(Screen):
    """Settings screen."""

    connection: reactive[ConnectionConfig | None] = reactive(None)

    def __init__(self, connection: ConnectionConfig | None = None, *args, **kwargs) -> None:
        """Construct a settings screen."""
        super().__init__(*args, **kwargs)
        self.connection = connection

    def compose(self) -> "ComposeResult":
        """Compose the widget."""
        yield Header()
        yield Footer()
        yield MainMenu(active_screen="Settings")
        yield Label("Settings Screen")
        yield Label(f"Connection: {self.connection}")

    def on_screen_resume(self, event: events.ScreenResume) -> None:
        """On screen resume."""
        self.app.sub_title = "Settings"
