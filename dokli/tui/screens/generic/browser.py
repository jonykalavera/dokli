"""Yazi-style 3-column browser over the schema-driven hierarchy."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

import httpx
from textual.binding import Binding
from textual.containers import Horizontal, VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer, Header, Input, Label

from dokli.api_client import APIClient
from dokli.config import ConnectionConfig
from dokli.tui.engine import (
    EntityRegistry,
    action_bindings,
    classify,
    collect_children,
    entity_icon,
    field_label,
    record_id,
    record_title,
)
from dokli.tui.screens.generic.execute import confirm_and_run
from dokli.tui.screens.generic.form import ActionFormScreen

if TYPE_CHECKING:
    from textual.app import ComposeResult


@dataclass
class Level:
    """One level of the navigation path."""

    kind: str  # "entities" | entity name | "children"
    items: list[dict]
    index: int = 0
    entity: str | None = None  # entity used to build this level
    record: dict | None = None  # parent record for "children" levels


class BrowserScreen(Screen):
    """3-column browser: parent | current | detail+actions."""

    CSS = """
    #current-pane > .selected, #parent-pane > .selected {
        background: $primary;
        color: $text;
    }
    """

    BINDINGS = [
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
        Binding("down", "cursor_down", "Down", show=False),
        Binding("up", "cursor_up", "Up", show=False),
        Binding("h", "left", "Parent"),
        Binding("l", "right", "Child", show=False),
        Binding("enter", "right", "Child"),
        Binding("r", "refresh", "Refresh"),
        Binding("/", "filter", "Filter"),
        Binding("escape", "cancel", "Back"),
        Binding("q", "quit", "Quit"),
    ]

    def __init__(
        self,
        connection: ConnectionConfig,
        registry: EntityRegistry,
        *args,
        **kwargs,
    ) -> None:
        """Construct the browser screen."""
        super().__init__(*args, **kwargs)
        self.connection = connection
        self.registry = registry
        self.client = APIClient(connection)
        entities = [{"_kind": name, "name": name} for name in registry.listable()]
        self.path = [Level(kind="entities", items=entities)]
        self._filter = ""

    def compose(self) -> "ComposeResult":
        """Compose the screen."""
        yield Header()
        yield Footer()
        yield Horizontal(
            VerticalScroll(id="parent-pane"),
            VerticalScroll(id="current-pane"),
            VerticalScroll(id="detail-pane"),
        )
        yield Input(placeholder="Filter...", id="filter")

    def on_screen_resume(self, event) -> None:
        """On screen resume."""
        self.app.sub_title = f"{self.connection.name} - Browser"
        self._rerender()

    def _rerender(self) -> None:
        """Schedule a re-render of the browser panes."""
        self.run_worker(self._refresh_all, exclusive=True)  # type: ignore[arg-type]

    # -- state ------------------------------------------------------------

    @property
    def current(self) -> Level:
        """The current level."""
        return self.path[-1]

    @property
    def parent_level(self) -> Level | None:
        """The parent level, if any."""
        return self.path[-2] if len(self.path) >= 2 else None

    @property
    def selected(self) -> dict | None:
        """The selected item of the current level."""
        level = self.current
        if 0 <= level.index < len(level.items):
            return level.items[level.index]
        return None

    def _selected_kind(self) -> str | None:
        selected = self.selected
        if not selected:
            return None
        return selected.get("_kind") or (self.current.kind if self.current.kind != "entities" else None)

    def _item_label(self, item: dict, level: Level) -> str:
        title = record_title(item)
        if level.kind == "entities":
            return f"{entity_icon(title)}  {title}"
        if level.kind == "children":
            return f"{entity_icon(item.get('_kind') or '')}  {title}"
        return title

    def _visible_items(self, level: Level) -> list[dict]:
        if not self._filter:
            return level.items
        query = self._filter.lower()
        return [
            item
            for item in level.items
            if query in record_title(item).lower() or query in str(item.get("_kind", "")).lower()
        ]

    # -- rendering --------------------------------------------------------

    async def _refresh_all(self) -> None:
        await self._render_pane("#parent-pane", self.parent_level)
        await self._render_pane("#current-pane", self.current)
        await self._render_detail()
        path = " → ".join(level.kind for level in self.path)
        sub_title = f"{self.connection.name} · {path}"
        selected = self.selected
        if selected:
            sub_title += f" · {record_title(selected)}"
        self.app.sub_title = sub_title

    async def _render_pane(self, container_id: str, level: Level | None) -> None:
        container = self.query_one(container_id, VerticalScroll)
        await container.remove_children()
        if level is None:
            return
        items = self._visible_items(level)
        widgets = []
        for n, item in enumerate(items):
            selected = "selected" if n == level.index else ""
            widgets.append(Label(self._item_label(item, level), classes=selected))
        await container.mount(*widgets)

    async def _render_detail(self) -> None:
        container = self.query_one("#detail-pane", VerticalScroll)
        await container.remove_children()
        selected = self.selected
        widgets: list[Label] = []
        if selected is None:
            widgets.append(Label("(empty)", classes="field"))
        else:
            kind = self._selected_kind() or ""
            if kind:
                widgets.append(Label(f"{entity_icon(kind)}  {kind}", classes="title"))
            widgets.append(Label(self._breadcrumb(), classes="subtitle"))
            for key, value in selected.items():
                if key in ("_kind", "id") or value in (None, [], {}):
                    continue
                widgets.append(Label(f"[b]{field_label(key)}:[/b] {self._fmt(value)}", classes="field"))
            children = collect_children(selected)
            if children:
                widgets.append(Label(f"Children ({len(children)})", classes="section"))
                for child_entity, child in children[:10]:
                    widgets.append(Label(f"  {entity_icon(child_entity)}  {record_title(child)}"))
            entity = self.registry.get(kind)
            if entity:
                bindings = action_bindings(entity)
                if bindings:
                    widgets.append(Label("Actions", classes="section"))
                    for action, key in bindings:
                        widgets.append(Label(f"  [{'b'}]{key or '-'}[/] {action.verb}"))
        await container.mount(*widgets)

    def _fmt(self, value) -> str:
        if isinstance(value, dict | list):
            return f"{type(value).__name__} ({len(value)})"
        text = str(value)
        if len(text) > 200:
            text = text[:200] + "..."
        return text.replace("\n", " ")

    def _breadcrumb(self) -> str:
        return " → ".join(level.kind for level in self.path)

    # -- navigation -------------------------------------------------------

    def action_cursor_down(self) -> None:
        """Move the cursor down."""
        if self.current.index < len(self.current.items) - 1:
            self.current.index += 1
            self._rerender()

    def action_cursor_up(self) -> None:
        """Move the cursor up."""
        if self.current.index > 0:
            self.current.index -= 1
            self._rerender()

    def action_left(self) -> None:
        """Drill out to the parent level."""
        if len(self.path) > 1:
            self.path.pop()
            self._rerender()

    async def action_right(self) -> None:
        """Drill into the selected item."""
        selected = self.selected
        if not selected:
            return
        entity_name = self._selected_kind() or ""
        entity = self.registry.get(entity_name)
        if entity is None:
            return
        if self.current.kind == "entities":
            action = entity.get("all")
            if action is None:
                self.notify(f"'{entity_name}' has no 'all' action.", severity="warning")
                return
            data = await self._api_get(action, {})
            if data is None:
                return
            records = data if isinstance(data, list) else data.get("items", [])
            items = [{"_kind": entity_name, **record} for record in records]
            self.path.append(Level(kind=entity_name, items=items, entity=entity_name))
        else:
            one_action = entity.get("one")
            record = selected
            if one_action is not None:
                params = {
                    param: selected.get(param) or record_id(selected, entity_name)
                    for param in one_action.param_names
                }
                params = {key: value for key, value in params.items() if value}
                if params:
                    enriched = await self._api_get(one_action, params)
                    if enriched:
                        record = enriched
            children = collect_children(record)
            if not children:
                self.notify(f"'{entity_name}' has no children.", severity="warning")
                return
            items = [{"_kind": child_entity, **child} for child_entity, child in children]
            self.path.append(Level(kind="children", items=items, entity=entity_name, record=record))
        self._rerender()

    async def action_refresh(self) -> None:
        """Reload the current level."""
        level = self.current
        if level.kind == "entities":
            return
        entity = self.registry.get(level.entity or "")
        if entity is None:
            return
        if level.kind == "children":
            record = level.record or (self.parent_level.record if self.parent_level else None)
            if record is None:
                return
            children = collect_children(record)
            level.items = [{"_kind": child_entity, **child} for child_entity, child in children]
        else:
            action = entity.get("all")
            if action is None:
                return
            data = await self._api_get(action, {})
            if data is None:
                return
            records = data if isinstance(data, list) else data.get("items", [])
            level.items = [{"_kind": level.entity, **record} for record in records]
        self._rerender()

    def action_filter(self) -> None:
        """Open the filter input."""
        filter_input = self.query_one("#filter", Input)
        filter_input.display = True
        filter_input.focus()

    def on_input_changed(self, event) -> None:
        """Filter the current list as the user types."""
        if event.input.id == "filter":
            self._filter = event.value
            self._rerender()

    def action_cancel(self) -> None:
        """Close the filter or drill out."""
        filter_input = self.query_one("#filter", Input)
        if self.focused is filter_input:
            filter_input.display = False
            self._filter = ""
            self._rerender()
        else:
            self.action_left()

    def action_quit(self) -> None:
        """Quit the app."""
        self.app.exit()

    # -- actions ----------------------------------------------------------

    def on_key(self, event) -> None:
        """Handle auto-generated action keybindings."""
        if isinstance(self.focused, Input):
            return
        if not event.character:
            return
        entity = self.registry.get(self._selected_kind() or "")
        if entity is None:
            return
        for action, key in action_bindings(entity):
            if key and key == event.character:
                self._run_action(action)
                event.stop()
                return

    def _run_action(self, action) -> None:
        if classify(action) == "form":
            self.app.push_screen(
                ActionFormScreen(self.connection, action, record=self.selected, classes="Entities")
            )
            return
        body = {}
        schema = action.request_schema
        if schema.get("properties") and self.selected:
            body = {
                key: value
                for key, value in self.selected.items()
                if key in schema["properties"] and value is not None
            }
        confirm_and_run(
            self,
            self.connection,
            action,
            body,
            on_success=self._rerender,
        )

    async def _api_get(self, action, params: dict):
        """Execute a GET-style action and return the JSON, or None on error."""
        try:
            response = self.client.request(action.method, action.route, params)
            return response.json()
        except httpx.HTTPError as err:
            self.notify(f"API error: {err}", severity="error", timeout=10)
            return None
