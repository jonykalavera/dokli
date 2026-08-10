"""Splash/loading screen shown while a connection is being prepared."""

from pathlib import Path
from typing import TYPE_CHECKING

from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Footer, Header, Label, Static

if TYPE_CHECKING:
    from textual.app import ComposeResult

ASCII_ART_PATH = Path(__file__).resolve().parent.parent / "asciiart"


class SplashScreen(Screen):
    """A splash screen with the Dokploy logo and a centered status box."""

    def __init__(self, *args, **kwargs) -> None:
        """Construct the splash screen."""
        super().__init__(*args, **kwargs)
        with open(ASCII_ART_PATH / "dokploy-logo-compact.txt") as logo:
            self._logo = "".join(logo.readlines())

    def compose(self) -> "ComposeResult":
        """Compose the splash: logo on top, centered status box below."""
        yield Header()
        yield Static(self._logo, id="splash-logo")
        yield Vertical(
            Vertical(Label("Connecting…", id="splash-status"), id="status-panel"),
            id="status-zone",
        )
        yield Footer()

    def set_status(self, text: str) -> None:
        """Update the splash status line (no-op once unmounted)."""
        if not self.is_mounted:
            return
        self.query_one("#splash-status", Label).update(text)
