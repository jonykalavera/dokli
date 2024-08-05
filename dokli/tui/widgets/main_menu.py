"""Main menu widget."""

from typing import TYPE_CHECKING

from textual import log
from textual.widgets import Static, Tab, Tabs

if TYPE_CHECKING:
    from textual.app import ComposeResult


class MainMenu(Static):
    """Main menu widget."""

    def __init__(self, active_screen: str | None = None, *args, **kwargs) -> None:
        """Construct a main menu."""
        super().__init__(*args, **kwargs)
        self.active_screen = active_screen

    def compose(self) -> "ComposeResult":
        """Compose the widget."""
        yield Tabs(
            Tab("Projects", id="Projects"),
            # Tab("Monitoring", id="Monitoring"),
            # Tab("Traefik", id="Traefik"),
            # Tab("Docker", id="Docker"),
            Tab("Settings", id="Settings"),
            active=self.active_screen,
        )

    def on_tabs_tab_activated(self, event: Tabs.TabActivated) -> None:
        """On tabs click."""
        log("TAB ACTIVATED", event.tab, self.app.screen.name, self.app.screen.classes)
        if (
            event.tab
            and event.tab.id
            and event.tab.id != self.active_screen
            and event.tab.id not in self.app.screen.classes
        ):
            self.app.push_screen(event.tab.id)
