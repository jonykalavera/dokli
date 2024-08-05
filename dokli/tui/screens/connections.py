"""Connections screen."""

import contextlib
from dataclasses import dataclass
from typing import TYPE_CHECKING

from textual import events, log
from textual.css.query import NoMatches
from textual.message import Message
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Label, ListItem, ListView

from dokli.config import ConnectionConfig
from dokli.tui.screens.connection import ConnectionResult, ConnectionScreen
from dokli.tui.widgets.list_item import AddItem

if TYPE_CHECKING:
    from textual.app import ComposeResult


class ConnectionWidget(ListItem):
    """A Dokploy Connection."""

    ICON = ""

    def __init__(self, connection: ConnectionConfig, *args, **kwargs) -> None:
        """Construct a connection widget."""
        super().__init__(*args, **kwargs)
        self.connection = connection

    def compose(self) -> "ComposeResult":
        """Create child widgets."""
        yield Label(self.ICON, id="icon")
        yield Label(self.connection.name, id="name", classes="title")
        yield Label(f" {self.connection.url}", id="url")
        yield Label(f" {self.connection.notes}" if self.connection.notes else "", id="notes")


class ConnectionsScreen(Screen):
    """Connections Screen."""

    connections: reactive[list[ConnectionConfig]] = reactive([])

    @dataclass
    class AddConnection(Message):
        """New connection message."""

        connection: ConnectionConfig

    @dataclass
    class UpdateConnection(Message):
        """Update connection message."""

        connection: ConnectionConfig

    @dataclass
    class DeleteConnection(Message):
        """Delete connection message."""

        connection: ConnectionConfig

    @dataclass
    class SetConnection(Message):
        """Set connection message."""

        connection: ConnectionConfig

    BINDINGS = [
        ("a", "add_connection", "Add Connection"),
        ("e", "edit_connection", "Edit Connection"),
        ("d", "delete_connection", "Delete Connection"),
    ]

    def __init__(self, connections: list[ConnectionConfig] | None = None) -> None:
        """Construct a connections screen."""
        super().__init__()
        self.connections = connections or []

    def compose(self) -> "ComposeResult":
        """Create child widgets for the app."""
        yield Header()
        yield Footer()
        yield ListView(
            *self._get_connection_widgets(),
            id="connections-list",
        )

    def on_screen_resume(self, event: events.ScreenResume) -> None:
        """On screen resume."""
        self.app.sub_title = "Connections"

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """On button click."""
        if event.button.id == "edit":
            assert isinstance(event.button.parent, ConnectionWidget)
            self._show_connection_screen(event.button.parent.connection)

    def _show_connection_screen(self, connection: ConnectionConfig | None = None) -> None:
        detail = ConnectionScreen(connection)
        self.app.push_screen(detail, self._edit_connection_callback)

    def action_edit_connection(self) -> None:
        """Edit connection."""
        list_view = self.query_one(ListView)
        if isinstance(list_view.highlighted_child, ConnectionWidget):
            self._show_connection_screen(list_view.highlighted_child.connection)

    def action_add_connection(self) -> None:
        """New connection."""
        detail = ConnectionScreen()
        self.app.push_screen(detail, self._add_connection_callback)

    def _add_connection_callback(self, result: ConnectionResult | None) -> None:
        if result and result.connection:
            self.connections = [*self.connections, result.connection]
            self.post_message(self.AddConnection(result.connection))

    def _edit_connection_callback(self, result: ConnectionResult | None) -> None:
        if not result or not result.connection:
            return
        message = (
            self.UpdateConnection(result.connection) if not result.delete else self.DeleteConnection(result.connection)
        )
        log("message", message)
        self.post_message(message)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Select cursor."""
        if event.item.id == "__add__":
            self.action_add_connection()
        elif event.item.id:
            idx = int(event.item.id.split("__")[-1])
            self.post_message(self.SetConnection(self.connections[idx]))

    def _get_connection_widgets(self) -> list[ConnectionWidget | AddItem]:
        return [
            *(ConnectionWidget(c, id=f"conn__{n}") for n, c in enumerate(self.connections or [])),
            AddItem(id="__add__", item_name="connection"),
        ]

    async def watch_connections(
        self,
        old_connections: list[ConnectionConfig] | None,
        new_connections: list[ConnectionConfig] | None,
    ) -> None:
        """Watch connections."""
        log("Connections changed", new_connections, self.connections)
        with contextlib.suppress(NoMatches):
            list = self.query_one(ListView)
            await list.clear()
            list.extend(self._get_connection_widgets())
