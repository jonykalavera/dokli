"""Generic record detail + child navigation + action picker."""

from typing import TYPE_CHECKING

import httpx
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer, Header, Label, ListItem, ListView, Static

from dokli.api_client import APIClient
from dokli.config import ConnectionConfig
from dokli.tui.engine import (
    DESTRUCTIVE_VERBS,
    EntityRegistry,
    classify,
    field_label,
    nested_child_entity,
    record_id,
    record_title,
)
from dokli.tui.screens.generic.execute import confirm_and_run
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


class ChildItem(ListItem):
    """A nested child record (drill-down)."""

    def __init__(self, child_entity: str, record: dict, *args, **kwargs) -> None:
        """Construct a child item."""
        super().__init__(*args, **kwargs)
        self.child_entity = child_entity
        self.record = record

    def compose(self) -> "ComposeResult":
        """Compose the widget."""
        yield Label(f"{self.child_entity} · {record_title(self.record)}", id="name", classes="title")


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
    """Show a record, its nested children and its actions."""

    BINDINGS = [
        Binding("r", "refresh", "Refresh"),
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
        yield Label("Children", id="children-title")
        yield ListView(id="children")
        yield Label("Fields", id="fields-title")
        yield VerticalScroll(id="fields")
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
        self.action_refresh()

    def action_refresh(self) -> None:
        """Refresh the record detail."""
        self.run_worker(self._load(), exclusive=True)

    async def _load(self) -> None:
        entity = self.registry.get(self.entity_name)
        action = entity.get("one") if entity else None
        if action is not None:
            params = self._action_params(action)
            if params:
                client = APIClient(self.connection)
                try:
                    response = client.request("GET", action.route, params)
                    self.record = response.json()
                except httpx.HTTPError as err:
                    self.notify(f"API error: {err}", severity="error", timeout=10)
        await self._refresh_view()

    def _action_params(self, action) -> dict:
        params = {}
        for param in action.param_names:
            value = self.record.get(param) or record_id(self.record, self.entity_name)
            if value:
                params[param] = value
        return params

    async def _refresh_view(self) -> None:
        await self._render_children()
        await self._render_fields()
        await self._render_actions()

    def _collect_children(self) -> list[tuple[str, dict]]:
        children = []
        for key, records in self.record.items():
            child_entity = nested_child_entity(key)
            if not child_entity or not isinstance(records, list):
                continue
            for record in records:
                if isinstance(record, dict):
                    children.append((child_entity, record))
        return children

    async def _render_children(self) -> None:
        children = self._collect_children()
        list_view = self.query_one("#children", ListView)
        await list_view.clear()
        list_view.extend(
            [
                ChildItem(entity, record, id=f"child__{n}")
                for n, (entity, record) in enumerate(children)
            ]
        )
        self.query_one("#children-title").display = bool(children)
        if children:
            list_view.focus()

    async def _render_fields(self) -> None:
        container = self.query_one("#fields", VerticalScroll)
        container.remove_children()
        await container.mount(*(FieldRow(key, value) for key, value in self.record.items()))

    async def _render_actions(self) -> None:
        entity = self.registry.get(self.entity_name)
        actions = list(entity.actions.values()) if entity else []
        list_view = self.query_one("#actions", ListView)
        await list_view.clear()
        form_actions = [a for a in actions if classify(a) == "form"]
        other_actions = [a for a in actions if classify(a) == "action"]
        list_view.extend(
            [
                *(ActionItem(a.verb, "form", id=f"action__{a.verb}") for a in form_actions),
                *(ActionItem(a.verb, "action", id=f"action__{a.verb}") for a in other_actions),
            ]
        )

    def on_list_view_selected(self, event) -> None:
        """Navigate or run the selected action."""
        if isinstance(event.item, ChildItem):
            self.app.push_screen(
                RecordScreen(
                    self.connection,
                    self.registry,
                    event.item.child_entity,
                    event.item.record,
                    classes="Entities",
                )
            )
            return
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
            self._confirm_action(action)

    def _confirm_action(self, action) -> None:
        """Confirm and run a non-form action (e.g. remove, deploy)."""
        body = {}
        schema = action.request_schema
        if schema.get("properties"):
            body = {
                key: value
                for key, value in self.record.items()
                if key in schema["properties"] and value is not None
            }
        if action.verb in DESTRUCTIVE_VERBS:

            def on_success() -> None:
                self.dismiss(None)

        else:
            on_success = self.action_refresh
        confirm_and_run(self, self.connection, action, body, on_success=on_success)
