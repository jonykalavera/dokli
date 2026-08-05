"""Generic record detail + action picker."""

from typing import TYPE_CHECKING

from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer, Header, Label, ListItem, ListView, Static

from dokli.config import ConnectionConfig
from dokli.tui.engine import EntityRegistry, classify, field_label, record_id
from dokli.tui.screens.generic.form import ActionFormScreen

if TYPE_CHECKING:
    from textual.app import ComposeResult


class FieldRow(Static):
    """A key/value row."""

    def __init__(self, key: str, value, *args, **kwargs) -> None:
        """Construct a field row."""
        super().__init__(*args, **kwargs)
        self.key = key
        self.value = value

    def render(self):
        """Render the row."""
        value = self.value
        if isinstance(value, dict | list):
            value = f"{type(value).__name__} ({len(value)})"
        return f"[b]{field_label(self.key)}:[/b] {value}"


class ActionItem(ListItem):
    """An action available on the record."""

    def __init__(self, verb: str, action_type: str, *args, **kwargs) -> None:
        """Construct an action item."""
        super().__init__(*args, **kwargs)
        self.verb = verb
        self.action_type = action_type

    def compose(self) -> "ComposeResult":
        """Compose the widget."""
        yield Label(self.verb, id="name", classes="title")
        yield Label(self.action_type, id="meta")


class RecordScreen(Screen):
    """Show a record and its actions."""

    BINDINGS = [
        Binding("escape", "cancel", "Back"),
    ]

    def __init__(
        self,
        connection: ConnectionConfig,
        registry: EntityRegistry,
        entity_name: str,
        record: dict,
        *args,
        **kwargs,
    ) -> None:
        """Construct the record screen."""
        super().__init__(*args, **kwargs)
        self.connection = connection
        self.registry = registry
        self.entity_name = entity_name
        self.record = record

    def compose(self) -> "ComposeResult":
        """Compose the screen."""
        yield Header()
        yield Footer()
        yield Label(self.record_title(), id="title", classes="title")
        yield VerticalScroll(
            *(FieldRow(key, value) for key, value in self.record.items()),
            id="fields",
        )
        yield Label("Actions", id="actions-title")
        yield ListView(id="actions")

    def record_title(self) -> str:
        """Title of the record."""
        for key in ("name", "appName", "title"):
            if self.record.get(key):
                return str(self.record[key])
        return str(record_id(self.record, self.entity_name) or self.entity_name)

    def on_screen_resume(self, event) -> None:
        """On screen resume."""
        self.app.sub_title = f"{self.connection.name} - {self.entity_name}"
        self._refresh()

    def _refresh(self) -> None:
        entity = self.registry.get(self.entity_name)
        actions = list(entity.actions.values()) if entity else []
        self._populate_actions(actions)

    def _populate_actions(self, actions) -> None:
        list_view = self.query_one("#actions", ListView)
        form_actions = [a for a in actions if classify(a) == "form"]
        other_actions = [a for a in actions if classify(a) != "form"]
        list_view.extend(
            [
                *(ActionItem(a.verb, "form", id=f"action__{a.verb}") for a in form_actions),
                *(ActionItem(a.verb, "action", id=f"action__{a.verb}") for a in other_actions),
            ]
        )
        list_view.focus()

    def on_list_view_selected(self, event) -> None:
        """Run the selected action."""
        if not isinstance(event.item, ActionItem):
            return
        entity = self.registry.get(self.entity_name)
        action = entity.get(event.item.verb) if entity else None
        if action is None:
            return
        if classify(action) == "form":
            self.app.push_screen(
                ActionFormScreen(self.connection, action, record=self.record, classes="Entities")
            )
        else:
            self.notify(f"'{action.verb}' action not implemented yet.", severity="warning")
