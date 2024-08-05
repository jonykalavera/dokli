"""Connections screen."""

import contextlib
from dataclasses import dataclass
from typing import TYPE_CHECKING

from textual import events, log
from textual.binding import Binding
from textual.containers import Horizontal
from textual.css.query import NoMatches
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.widgets import Button, Footer, Header, Input, Rule

from dokli.config import ConnectionConfig
from dokli.tui.forms import Form

if TYPE_CHECKING:
    from textual.app import ComposeResult


@dataclass
class ConnectionResult:
    """Connection screen result."""

    connection: ConnectionConfig | None = None
    delete: bool = False


class ConnectionScreen(ModalScreen[ConnectionResult]):
    """Connection Screen."""

    connection: reactive[ConnectionConfig | None] = reactive(None)

    def __init__(self, connection: ConnectionConfig | None = None, focus_on_resume=False, *args, **kwargs) -> None:
        """Construct a connection screen."""
        super().__init__(*args, **kwargs)
        self.connection = connection
        self.focus_on_resume = focus_on_resume

    BINDINGS = [
        Binding(
            "s",
            "save",
            "Save",
        ),
        Binding("d", "delete", "Delete"),
        Binding("c", "cancel", "Cancel"),
    ]

    def compose(self) -> "ComposeResult":
        """Create child widgets for the app."""
        yield Header()
        yield Footer()
        yield Form.from_model(ConnectionConfig, self.connection)
        yield Rule()
        yield Horizontal(
            Button("Save", variant="success", id="save"),
            Button(
                "Delete",
                variant="error",
                id="delete",
                classes="hidden" if self.connection is None else "",
            ),
            Button(
                "Cancel",
                variant="default",
                id="cancel",
            ),
        )

    def watch_connection(self, old_value: ConnectionConfig | None, new_value: ConnectionConfig) -> None:
        """Watch connection changes."""
        self.app.sub_title = "New Connection" if not new_value else f"Edit Connection: {new_value.name}"
        log("ConnectionScreen", self.connection)

    def action_save(self) -> None:
        """Save connection."""
        form = self.query_one(Form)
        if form.is_valid:
            self.dismiss(ConnectionResult(form.instance, False))

    def action_delete(self) -> None:
        """Delete connection."""
        self.dismiss(ConnectionResult(self.connection, True))

    def action_cancel(self) -> None:
        """Cancel."""
        self.dismiss(ConnectionResult(self.connection, False))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """On button pressed."""
        action = getattr(self, f"action_{event.button.id}", None)
        if not action:
            log("No action", event.button.id)
            return
        action()

    def on_screen_resume(self, event: events.ScreenResume) -> None:
        """On screen resume."""
        log("on screen resume", self.connection)
        if self.focus_on_resume:
            with contextlib.suppress(NoMatches):
                self.query(Input).first().focus()

    def on_screen_suspend(self, event: events.ScreenSuspend) -> None:
        """On screen suspend."""
        self.query_one(Form).reset()
