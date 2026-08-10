"""Splash/loading screen shown while a connection is being prepared."""

from pathlib import Path
from typing import TYPE_CHECKING

from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Footer, Header, Label, Static

if TYPE_CHECKING:
    from textual.app import ComposeResult

ASCII_ART_PATH = Path(__file__).resolve().parent.parent / "asciiart"

# Braille spinner frames, shown one at a time before the status text.
SPINNER_FRAMES = ["⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷"]
_SPINNER_INTERVAL = 0.12


class SplashScreen(Screen):
    """A splash screen with the Dokploy logo as backdrop and a centered status box."""

    def __init__(self, *args, **kwargs) -> None:
        """Construct the splash screen."""
        super().__init__(*args, **kwargs)
        with open(ASCII_ART_PATH / "dokploy-logo-notext.txt") as logo:
            self._logo = "".join(logo.readlines())
        self._status = "Connecting…"
        self._frame = 0
        self._spinner = None

    def compose(self) -> "ComposeResult":
        """Compose the splash: the logo fills the screen, status box floats on top."""
        yield Header()
        yield Footer()
        yield Static(self._logo, id="splash-logo")
        yield Vertical(Label(f"{SPINNER_FRAMES[0]} {self._status}", id="splash-status"), id="status-panel")

    def on_mount(self) -> None:
        """Start the spinner animation."""
        self._spinner = self.set_interval(_SPINNER_INTERVAL, self._advance_spinner)

    def on_unmount(self) -> None:
        """Stop the spinner animation."""
        if self._spinner is not None:
            self._spinner.stop()

    def _advance_spinner(self) -> None:
        self._frame = (self._frame + 1) % len(SPINNER_FRAMES)
        self._render_status()

    def set_status(self, text: str) -> None:
        """Update the splash status line (no-op once unmounted)."""
        self._status = text
        self._render_status()

    def _render_status(self) -> None:
        if not self.is_mounted:
            return
        self.query_one("#splash-status", Label).update(f"{SPINNER_FRAMES[self._frame]} {self._status}")
