"""Generic confirmation screen for mutating actions."""

from typing import TYPE_CHECKING

from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Label

if TYPE_CHECKING:
    from textual.app import ComposeResult


class ConfirmScreen(Screen):
    """Ask for explicit confirmation before running an action.

    Dismisses with ``True`` (confirmed) or ``False`` (cancelled).
    """

    BINDINGS = [
        Binding("y", "confirm", "Yes"),
        Binding("n", "cancel", "No"),
        Binding("escape", "cancel", "No"),
    ]

    def __init__(self, title: str, message: str, danger: bool = False, *args, **kwargs) -> None:
        """Construct the confirmation screen."""
        super().__init__(*args, **kwargs)
        self._title = title
        self._message = message
        self._danger = danger

    def compose(self) -> "ComposeResult":
        """Compose the screen."""
        yield Header()
        yield Footer()
        yield Label(self._title, id="title", classes="title")
        yield Label(self._message, id="message")
        yield Button("Yes", id="yes", variant="error" if self._danger else "primary")
        yield Button("No", id="no")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle buttons."""
        if event.button.id == "yes":
            self.dismiss(True)
        elif event.button.id == "no":
            self.dismiss(False)

    def action_confirm(self) -> None:
        """Confirm the action."""
        self.dismiss(True)

    def action_cancel(self) -> None:
        """Cancel the action."""
        self.dismiss(False)
