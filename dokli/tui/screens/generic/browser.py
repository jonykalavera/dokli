"""Yazi-style 3-column browser over the schema-driven hierarchy."""

import asyncio
import contextlib
from dataclasses import dataclass
from typing import TYPE_CHECKING

import httpx
from textual.binding import Binding
from textual.containers import Horizontal, VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer, Header, Input, Label, LoadingIndicator

from dokli.api_client import APIClient
from dokli.config import ConnectionConfig
from dokli.tui.engine import (
    EntityRegistry,
    action_bindings,
    classify,
    collect_children,
    field_label,
    icon_label,
    key_for_verb,
    list_verb_override,
    nested_child_entity,
    param_source,
    record_id,
    record_title,
    related_action_spec,
    related_records,
    related_spec,
    state_indicator,
)
from dokli.tui.engine.related import PARENT_ACTIONS, RELATED_ACTIONS
from dokli.tui.engine.schemas import AMBIENT_ID_FIELDS, CHILD_ENTITIES
from dokli.tui.engine.spec import PRIORITY_ENTITIES
from dokli.tui.screens.generic.execute import confirm_and_run
from dokli.tui.screens.generic.form import ActionFormScreen
from dokli.tui.screens.generic.picker import PickerScreen
from dokli.tui.screens.generic.result import ResultScreen

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
    #parent-pane { width: 2fr; }
    #current-pane { width: 2fr; }
    #detail-pane { width: 4fr; }
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
        Binding("right", "right", "Child", show=False),
        Binding("f5", "refresh", "Refresh"),
        Binding("/", "filter", "Filter"),
        Binding("escape", "cancel", "Back"),
        Binding("q", "quit", "Quit"),
    ]

    def __init__(
        self,
        connection: ConnectionConfig,
        registry: EntityRegistry,
        entity_order: list[str] | None = None,
        client: APIClient | None = None,
        *args,
        **kwargs,
    ) -> None:
        """Construct the browser screen.

        ``client`` is an already-built API client (schema fetched). When not
        provided, it is built here — callers should pre-build it off the event
        loop so the schema fetch never blocks the UI.
        """
        super().__init__(*args, **kwargs)
        self.connection = connection
        self.registry = registry
        self.client = client if client is not None else APIClient(connection)
        self.entity_order = tuple(entity_order or ())
        entities = [{"_kind": name, "name": name} for name in self._listable_entities()]
        self.path = [Level(kind="entities", items=entities)]
        self._filter = ""
        self._related_cache: dict[str, list[dict]] = {}

    def _listable_entities(self) -> list[str]:
        """The top-level entity list, honoring the configured priority order."""
        priority = self.entity_order or PRIORITY_ENTITIES
        return self.registry.listable(priority=priority)

    def compose(self) -> "ComposeResult":
        """Compose the screen."""
        yield Header()
        yield Footer()
        yield Horizontal(
            VerticalScroll(id="parent-pane"),
            VerticalScroll(id="current-pane"),
            VerticalScroll(id="detail-pane"),
        )
        yield LoadingIndicator(id="loading", classes="spinner")
        yield Input(placeholder="Filter...", id="filter")

    def _set_loading(self, loading: bool) -> None:
        """Show or hide the loading spinner."""
        with contextlib.suppress(Exception):
            self.query_one("#loading", LoadingIndicator).display = loading

    async def on_mount(self) -> None:
        """On mount, render the entity list immediately."""
        await self._refresh_all()

    def reload(
        self,
        connection: ConnectionConfig,
        registry: EntityRegistry,
        entity_order: list[str] | None = None,
        client: APIClient | None = None,
    ) -> None:
        """Point this browser at a new connection/registry."""
        self.connection = connection
        self.registry = registry
        self.client = client if client is not None else APIClient(connection)
        if entity_order is not None:
            self.entity_order = tuple(entity_order)
        entities = [{"_kind": name, "name": name} for name in self._listable_entities()]
        self.path = [Level(kind="entities", items=entities)]
        self._filter = ""
        self._related_cache = {}
        self.run_worker(self._refresh_current, exclusive=True)  # type: ignore[arg-type]

    def on_screen_resume(self, event) -> None:
        """On screen resume."""
        self.app.sub_title = f"{self.connection.name} - Browser"
        self.run_worker(self._refresh_current, exclusive=True)  # type: ignore[arg-type]

    def _rerender(self) -> None:
        """Schedule a re-render of the browser panes."""
        self.run_worker(self._refresh_all, exclusive=True)  # type: ignore[arg-type]

    async def _refresh_current(self) -> None:
        """Reload the current level's data, then re-render."""
        if self.current.kind == "entities":
            await self._refresh_all()
        else:
            await self.action_refresh()

    def _refresh_after_action(self) -> None:
        """Schedule a reload of the current level (used after actions/forms)."""
        self.run_worker(self._refresh_current, exclusive=True)  # type: ignore[arg-type]

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
        """The selected item of the current level (within the visible/filtered list)."""
        items = self._visible_items(self.current)
        if 0 <= self.current.index < len(items):
            return items[self.current.index]
        return None

    def _selected_kind(self) -> str | None:
        selected = self.selected
        kind = selected.get("_kind") if selected else None
        if kind:
            return kind
        # Empty lists (e.g. a category with no records yet) still know their kind.
        return self.current.kind if self.current.kind != "entities" else None

    async def _related_records(self, record: dict) -> list[dict]:
        """Related records of a selected record, cached by record identity."""
        kind = self.current.entity or self._selected_kind() or ""
        key = f"{kind}:{record_id(record, kind)}"
        if key not in self._related_cache:
            self._related_cache[key] = await asyncio.to_thread(
                related_records, self.client, self.registry, kind, record
            )
        return self._related_cache[key]

    def _item_label(self, item: dict, level: Level) -> str:
        title = record_title(item)
        if level.kind == "entities":
            return f"{icon_label(title)}  {title}"
        if level.kind == "categories":
            label = item.get("label") or title
            count = item.get("count")
            suffix = f" ({count})" if count else ""
            return f"{icon_label(item.get('_kind') or '')}  {label}{suffix}"
        if level.kind == "children":
            return f"{icon_label(item.get('_kind') or '')}  {title}"
        return f"{icon_label(level.kind)}  {title}"

    def _visible_items(self, level: Level) -> list[dict]:
        items = level.items
        if not self._filter:
            return items
        query = self._filter.lower()
        return [
            item
            for item in items
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
            header, title_key = self._record_header(selected, kind)
            if header:
                widgets.append(Label(header, classes="title"))
            widgets.append(Label(self._breadcrumb(), classes="subtitle"))
            skip = {"_kind", "id"}
            if title_key:
                skip.add(title_key)
            widgets.extend(self._detail_field_labels(selected, skip))
            children = collect_children(selected)
            if children:
                widgets.append(Label(f"Children ({len(children)})", classes="section"))
                for child_entity, child in children[:10]:
                    widgets.append(Label(f"  {icon_label(child_entity)}  {record_title(child)}"))
            related = await self._related_records(selected)
            if related:
                spec = related_spec(kind)
                label = spec["label"] if spec else "Related"
                widgets.append(Label(f"{label} ({len(related)})", classes="section"))
                for item in related[:10]:
                    title = item.get("name") or record_id(item) or "?"
                    state = item.get("state") or ""
                    status = item.get("status") or ""
                    suffix = f" ({state})" if state else (f" ({status})" if status else "")
                    widgets.append(Label(f"  {state_indicator(state)} {title}{suffix}"))
        await container.mount(*widgets)

    def _detail_field_labels(self, selected: dict, skip: set[str]) -> list[Label]:
        """Field labels for a record, excluding the skip set and empty values."""
        labels = []
        for key, value in selected.items():
            if key in skip or value in (None, [], {}):
                continue
            labels.append(Label(f"[b]{field_label(key)}:[/b] {self._fmt(value)}", classes="field"))
        return labels

    def _record_header(self, selected: dict, kind: str) -> tuple[str | None, str | None]:
        """The detail header label and the title key to skip in the field list."""
        title_key = next(
            (key for key in ("name", "appName", "title", "label") if selected.get(key)),
            None,
        )
        if not kind:
            return None, title_key
        header = f"{icon_label(kind)}  {kind}"
        if title_key:
            header += f"  [b]·  {self._fmt(selected[title_key])}[/b]"
        return header, title_key

    def _entity_bindings(self, entity) -> list:
        """Action keybindings for an entity.

        At the top-level entity list the "selected" item is a synthetic record,
        so only actions that do not need an existing record are exposed:
        create/new and read-only GET queries. Once inside a real record, all
        actions (update, remove, ...) are available, plus the contextual
        related-entity actions declared in ``RELATED_ACTIONS``.
        """
        keybindings = getattr(self.app, "tui_keybindings", lambda: {})()
        bindings = action_bindings(entity, **keybindings)
        if self.current.kind == "categories":
            # At the category picker, only the parent record's own actions apply.
            return bindings
        if self.current.kind != "entities":
            taken = {key for _, key in bindings if key}
            for spec in RELATED_ACTIONS.get(self._selected_kind() or "", []):
                rel_entity = self.registry.get(spec["entity"])
                rel_action = rel_entity.get(spec["verb"]) if rel_entity else None
                if rel_action is None:
                    continue
                key = spec.get("key") or key_for_verb(spec["verb"], frozenset(taken), **keybindings)
                if key:
                    taken.add(key)
                bindings.append((rel_action, key))
            for spec in PARENT_ACTIONS.get(self._selected_kind() or "", []):
                parent_action = self._parent_action(spec)
                if parent_action is None:
                    continue
                key = spec.get("key") or key_for_verb(spec["verb"], frozenset(taken), **keybindings)
                if key:
                    taken.add(key)
                bindings.append((parent_action, key))
            return bindings
        return [
            (action, key) for action, key in bindings if action.verb in ("create", "new") or action.method == "GET"
        ]

    def contextual_bindings(self) -> list[tuple[str, str]]:
        """The current selection's action keybindings, for the help screen."""
        entries: list[tuple[str, str]] = []
        entity = self.registry.get(self._selected_kind() or "")
        if entity is None:
            return entries
        selected = self.selected or {}
        title = record_title(selected) if selected else ""
        for action, key in self._entity_bindings(entity):
            if key:
                label = self._action_verb_label(action)
                if title:
                    label = f"{label} {title}"
                entries.append((key, label))
        return entries

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
        """Move the cursor down (within the visible/filtered list)."""
        visible = self._visible_items(self.current)
        if self.current.index < len(visible) - 1:
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
            self._reset_filter()
            self._rerender()

    def _reset_filter(self) -> None:
        """Clear the active filter when navigating to a new level."""
        self._filter = ""
        filter_input = self.query_one("#filter", Input)
        filter_input.display = False
        filter_input.value = ""

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
            await self._drill_entity(entity_name, entity)
        elif self.current.kind == "categories":
            await self._open_category(selected, self.current.record or {})
            self._reset_filter()
            self._rerender()
            return
        else:
            await self._drill_record(selected, entity_name, entity)
        self._reset_filter()
        self._rerender()

    async def _drill_entity(self, entity_name: str, entity) -> None:
        """List the records of a top-level entity."""
        list_verb = list_verb_override(entity_name) or "all"
        action = entity.get(list_verb)
        if action is None:
            self.notify(f"'{entity_name}' has no '{list_verb}' action.", severity="warning")
            return
        data = await self._api_get(action, {})
        if data is None:
            return
        records = data if isinstance(data, list) else data.get("items", [])
        items = [{"_kind": entity_name, **record} for record in records]
        self.path.append(Level(kind=entity_name, items=items, entity=entity_name))

    async def _drill_record(self, selected: dict, entity_name: str, entity) -> None:
        """Drill into a record: environments show services, others show categories."""
        one_action = entity.get("one")
        record = selected
        if one_action is not None:
            params = {
                param: selected.get(param) or record_id(selected, entity_name) for param in one_action.param_names
            }
            params = {key: value for key, value in params.items() if value}
            if params:
                enriched = await self._api_get(one_action, params)
                if enriched:
                    record = enriched
        if entity_name == "environment":
            # Environments are a per-project filter: drill straight to services.
            children = collect_children(record)
            if not children:
                self.notify(f"'{entity_name}' has no children.", severity="warning")
                return
            items = [{"_kind": child_entity, **child} for child_entity, child in children]
            self.path.append(Level(kind="children", items=items, entity=entity_name, record=record))
            return
        categories = self._record_categories(record)
        if not categories:
            self.notify(f"'{entity_name}' has no children.", severity="warning")
            return
        if len(categories) == 1:
            await self._open_category(categories[0], record)
        else:
            self.path.append(Level(kind="categories", items=categories, entity=entity_name, record=record))

    def _record_categories(self, record: dict) -> list[dict]:
        """The child categories of a record.

        Containers and related lists (e.g. deployments) are fetched lazily, so
        they carry no count; nested child arrays are already in the record and
        show their free count.
        """
        kind = self._selected_kind() or ""
        categories: list[dict] = []
        if related_spec(kind) is not None:
            categories.append({"_kind": "docker", "_category": "containers", "label": "Containers", "count": None})
        for spec in RELATED_ACTIONS.get(kind, []):
            categories.append(
                {
                    "_kind": spec["entity"],
                    "_category": "related",
                    "related_spec": spec,
                    "label": spec["label"],
                    "count": None,
                }
            )
        # Include nested child-array keys even when empty, so you can create the
        # first record of a category (e.g. a compose with no domains yet).
        for key, value in record.items():
            child_entity = nested_child_entity(key)
            if not child_entity or not isinstance(value, list):
                continue
            categories.append(
                {
                    "_kind": child_entity,
                    "_category": "nested",
                    "child_entity": child_entity,
                    "label": child_entity.title(),
                    "count": len(value),
                }
            )
        return categories

    async def _open_category(self, category: dict, record: dict) -> None:
        """Open a child category, fetching its records on demand."""
        parent_kind = self.current.entity or ""
        cat = category["_category"]
        if cat == "containers":
            containers = await self._related_records(record)
            items = [{"_kind": "docker", **container} for container in containers]
            self.path.append(Level(kind="containers", items=items, entity=parent_kind, record=record))
            return
        if cat == "related":
            await self._open_related(category["related_spec"], record, parent_kind)
            return
        child_entity = category["child_entity"]
        children = [child for entity, child in collect_children(record) if entity == child_entity]
        items = [{"_kind": child_entity, **child} for child in children]
        self.path.append(Level(kind=child_entity, items=items, entity=parent_kind, record=record))

    async def _open_related(self, spec: dict, record: dict, parent_kind: str) -> None:
        """Open a RELATED_ACTIONS category (e.g. deployments of a service)."""
        rel_entity = self.registry.get(spec["entity"])
        action = rel_entity.get(spec["verb"]) if rel_entity else None
        if action is None:
            self.notify(f"'{spec['entity']}' has no '{spec['verb']}' action.", severity="warning")
            return
        params = {}
        for param, field in spec["fill"].items():
            value = record.get(field)
            if value:
                params[param] = value
        missing = [param for param in action.required_params if not params.get(param)]
        if missing:
            await self._resolve_missing(action, params, missing)
            return
        data = await self._api_get(action, params)
        if data is None:
            return
        records = data if isinstance(data, list) else data.get("items", [])
        items = [{"_kind": spec["entity"], **item} for item in records if isinstance(item, dict)]
        if not items:
            self.notify(f"No {spec['label'].lower()} found.", severity="warning")
            return
        self.path.append(Level(kind=spec["entity"], items=items, entity=parent_kind, record=record))

    async def action_refresh(self) -> None:
        """Reload the current level (re-probing entity usability at the top)."""
        self._set_loading(True)
        try:
            await self._action_refresh()
        finally:
            self._set_loading(False)

    async def _action_refresh(self) -> None:
        """Reload the current level's data."""
        level = self.current
        if level.kind == "entities":
            await self._refresh_all()
            return
        self._related_cache.clear()
        entity = self.registry.get(level.entity or "")
        if entity is None:
            return
        if level.kind == "children":
            record = level.record or (self.parent_level.record if self.parent_level else None)
            if record is None:
                return
            one_action = entity.get("one")
            if one_action is not None:
                params = {
                    param: record.get(param) or record_id(record, entity.name) for param in one_action.param_names
                }
                params = {key: value for key, value in params.items() if value}
                if params:
                    enriched = await self._api_get(one_action, params)
                    if enriched:
                        record = enriched
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
        if level.index >= len(level.items):
            level.index = max(0, len(level.items) - 1)
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
            self._clamp_index()
            self._rerender()

    def _clamp_index(self) -> None:
        """Keep the cursor within the visible (filtered) items."""
        visible = self._visible_items(self.current)
        if self.current.index >= len(visible):
            self.current.index = max(0, len(visible) - 1)

    def action_cancel(self) -> None:
        """Close the filter or drill out."""
        filter_input = self.query_one("#filter", Input)
        if self.focused is filter_input:
            self._confirm_filter(clear=True)
        else:
            self.action_left()

    def _confirm_filter(self, clear: bool = False) -> None:
        """Close the filter, keeping the applied filter (or clearing it)."""
        filter_input = self.query_one("#filter", Input)
        filter_input.display = False
        if clear:
            filter_input.value = ""
            self._filter = ""
        self._clamp_index()
        self._rerender()

    def action_quit(self) -> None:
        """Quit the app."""
        self.app.exit()

    # -- actions ----------------------------------------------------------

    def on_key(self, event) -> None:
        """Handle enter (filter confirm / drill) and auto-generated action keys."""
        filter_input = self.query_one("#filter", Input)
        if self.focused is filter_input:
            if event.key == "enter":
                self._confirm_filter()
                event.stop()
            return
        if event.key == "enter":
            self.run_worker(self.action_right, exclusive=True)  # type: ignore[arg-type]
            event.stop()
            return
        if not event.character and not event.key:
            return
        entity = self.registry.get(self._selected_kind() or "")
        if entity is None:
            return
        for action, key in self._entity_bindings(entity):
            if key and key in (event.character, event.key):
                self._run_action(action)
                event.stop()
                return

    def _run_action(self, action) -> None:
        if classify(action) == "form":
            self.run_worker(self._open_form(action), exclusive=True, group="action")  # type: ignore[arg-type]
            return
        if action.method == "GET":
            if self._related_action_spec(action.route) is not None:
                self.run_worker(self._show_related_list(action), exclusive=True, group="action")  # type: ignore[arg-type]
            elif self._parent_action_spec(action.route) is not None:
                self.run_worker(self._show_parent_action(action), exclusive=True, group="action")  # type: ignore[arg-type]
            else:
                self.run_worker(self._show_result(action), exclusive=True, group="action")  # type: ignore[arg-type]
            return
        body = {}
        schema = action.request_schema
        if schema.get("properties") and self.selected:
            body = {
                key: value for key, value in self.selected.items() if key in schema["properties"] and value is not None
            }
        confirm_and_run(
            self,
            self.connection,
            action,
            body,
            on_success=self._refresh_after_action,
        )

    def _build_params(self, action) -> tuple[dict, list[str]]:
        """Params derivable from the selected record, plus the missing required ones."""
        params = {}
        record = self.selected or {}
        entity = self.registry.get(self._selected_kind() or "")
        entity_name = entity.name if entity else ""
        for param in action.param_names:
            value = record.get(param)
            # Only backfill the entity's own id (for records that use a plain
            # ``id``); never inject it into other params like ``containerId``,
            # ``tail`` or ``since``, which would make the request invalid.
            if not value and param == f"{entity_name}Id":
                value = record_id(record, entity_name)
            if value:
                params[param] = value
        missing = [param for param in action.required_params if not params.get(param)]
        return params, missing

    async def _show_result(self, action) -> None:
        """Run a read-only GET action and show its result."""
        params, missing = self._build_params(action)
        if missing:
            await self._resolve_missing(action, params, missing)
            return
        data = await self._api_get(action, params)
        if data is not None:
            self.app.push_screen(ResultScreen(self.connection, action, data, params=params, classes="Entities"))

    def _related_action_spec(self, route: str) -> dict | None:
        """The RELATED_ACTIONS spec for the selected record matching ``route``, if any."""
        return related_action_spec(self._selected_kind() or "", route)

    def _parent_action(self, spec: dict):
        """The parent service's action named by a PARENT_ACTIONS spec."""
        parent_name = self.current.entity or ""
        parent_entity = self.registry.get(parent_name)
        return parent_entity.get(spec["verb"]) if parent_entity else None

    def _parent_action_spec(self, route: str) -> dict | None:
        """The PARENT_ACTIONS spec whose parent action route matches ``route``, if any."""
        for spec in PARENT_ACTIONS.get(self._selected_kind() or "", []):
            action = self._parent_action(spec)
            if action is not None and action.route == route:
                return spec
        return None

    def _action_verb_label(self, action) -> str:
        """The display name for an action, prefixed with its entity when contextual."""
        spec = self._related_action_spec(action.route)
        if spec:
            return f"{spec['entity']}.{action.verb}"
        if self._parent_action_spec(action.route) is not None:
            return f"{self.current.entity or ''}.{action.verb}"
        return action.verb

    async def _show_related_list(self, action) -> None:
        """Run a contextual related list action into a navigable records list."""
        spec = self._related_action_spec(action.route)
        if spec is None:
            await self._show_result(action)
            return
        params, missing = self._build_params(action)
        if missing:
            await self._resolve_missing(action, params, missing)
            return
        data = await self._api_get(action, params)
        if data is None:
            return
        records = data if isinstance(data, list) else data.get("items", [])
        items = [{"_kind": spec["entity"], **record} for record in records if isinstance(record, dict)]
        if not items:
            self.notify(f"No {spec['label'].lower()} found.", severity="warning")
            return
        self.path.append(
            Level(kind=spec["entity"], items=items, entity=self.current.entity, record=self.selected or {})
        )
        self._reset_filter()
        self._rerender()

    async def _show_parent_action(self, action) -> None:
        """Run a parent action (e.g. the service's readLogs).

        Params are filled from the child record and the parent service record.
        """
        spec = self._parent_action_spec(action.route)
        if spec is None:
            await self._show_result(action)
            return
        parent_name = self.current.entity or ""
        parent_record = self.current.record or {}
        params = {}
        for param, field in spec["fill"].items():
            value = (self.selected or {}).get(field)
            if value:
                params[param] = value
        parent_id = f"{parent_name}Id"
        value = parent_record.get(parent_id)
        if value:
            params[parent_id] = value
        missing = [param for param in action.required_params if not params.get(param)]
        if missing:
            await self._resolve_missing(action, params, missing)
            return
        data = await self._api_get(action, params)
        if data is not None:
            self.app.push_screen(ResultScreen(self.connection, action, data, params=params, classes="Entities"))

    async def _resolve_missing(self, action, params: dict, missing: list[str]) -> None:
        """Satisfy missing required params (e.g. containerId) via a picker."""
        source = param_source(missing[0])
        kind = self._selected_kind() or ""
        spec = related_spec(kind)
        record = self.selected or {}
        if source is None or spec is None:
            self.notify(
                f"Missing required: {', '.join(missing)} (not in the record)",
                severity="warning",
                timeout=10,
            )
            return
        candidates = await asyncio.to_thread(related_records, self.client, self.registry, kind, record)
        if not candidates:
            self.notify(
                f"No {spec['label']} found for '{record_title(record)}'.",
                severity="warning",
                timeout=10,
            )
            return
        value_field = source["value_field"]
        items = [candidate for candidate in candidates if candidate.get(value_field)]
        value = await self.app.push_screen_wait(
            PickerScreen(
                f"Select {spec['label']} for {action.route}",
                items,
                value_field,
                source["label_field"],
                classes="Entities",
            )
        )
        if value is None:
            return
        params[missing[0]] = value
        data = await self._api_get(action, params)
        if data is not None:
            self.app.push_screen(ResultScreen(self.connection, action, data, params=params, classes="Entities"))

    def _create_prefill(self, action) -> dict:
        """Prefill a create form with the parent service id.

        When opened from a service's child category (e.g. a domain under a
        compose) the parent id and any curated fields are prefilled.
        """
        parent_kind = self.current.entity or ""
        parent_record = self.current.record or {}
        prefill: dict = {}
        if not parent_kind or not parent_record:
            return prefill
        parent_id = f"{parent_kind}Id"
        value = parent_record.get(parent_id)
        if value:
            prefill[parent_id] = value
        if action.route == "domain.create" and parent_kind == "compose":
            prefill["domainType"] = "compose"
        return prefill

    def _parent_id_candidates(self, action, entity_name: str) -> set[str]:
        """The parent-id fields of a child schema (foreign keys to a parent).

        Every ``*Id`` property that is not the entity's own id nor an ambient
        id is a mutually-exclusive parent reference — only for curated child
        entities. Service entities' own forms keep their FK fields editable.
        """
        if entity_name not in CHILD_ENTITIES:
            return set()
        props = set(action.request_schema.get("properties", {}))
        own = f"{entity_name}Id"
        return {field for field in props if field.endswith("Id") and field != own and field not in AMBIENT_ID_FIELDS}

    def _form_id_handling(self, action, entity_name: str, record: dict) -> tuple[set[str], dict]:
        """Id fields to hide from a form, and the ones to inject.

        Parent-id fields are hidden only with a parent context (and only for
        curated child entities). The entity's own primary key is always hidden —
        auto-generated on create, injected back from the record on update.
        """
        excluded = set()
        if self.current.record:
            excluded |= self._parent_id_candidates(action, entity_name)
        own = f"{entity_name}Id"
        if own in action.request_schema.get("properties", {}):
            excluded.add(own)
        inject = {field: record[field] for field in excluded if record.get(field)}
        return excluded, inject

    async def _open_form(self, action) -> None:
        """Open an action form.

        Create actions start with the parent service id prefilled (when opened
        from a service's child category); update/save/edit actions are enriched
        with the full record via ``one`` when available. Parent-id fields are
        hidden from the form and injected from context.
        """
        entity_name = self._selected_kind() or ""
        record: dict = {}
        if action.verb in ("create", "new"):
            record = self._create_prefill(action)
        else:
            record = self.selected or {}
            entity = self.registry.get(entity_name)
            one_action = entity.get("one") if entity else None
            if entity is not None and one_action is not None:
                params = {
                    param: record.get(param) or record_id(record, entity.name) for param in one_action.param_names
                }
                params = {key: value for key, value in params.items() if value}
                if params:
                    enriched = await self._api_get(one_action, params)
                    if enriched:
                        record = enriched
        excluded, inject = self._form_id_handling(action, entity_name, record)
        self.app.push_screen(
            ActionFormScreen(
                self.connection,
                action,
                record=record,
                on_success=self._auto_deploy_callback(action),
                excluded=excluded,
                inject=inject,
                classes="Entities",
            )
        )

    def _auto_deploy_callback(self, action):
        """A form success hook that deploys the service when configured."""
        config = getattr(self.app, "config", None)
        if config is None or not config.tui.auto_deploy:
            return None
        if action.verb not in ("create", "new", "update", "edit", "save"):
            return None
        entity = self.registry.get(self._selected_kind() or "")
        deploy = entity.get("deploy") if entity else None
        if deploy is None:
            return None
        return lambda: self.run_worker(self._deploy_after_save(deploy), group="action")

    async def _deploy_after_save(self, deploy) -> None:
        """Refresh the list, then trigger a deploy of the (likely) saved record."""
        await self._refresh_current()
        entity_name = deploy.route.split(".")[0]
        entity_id = record_id(self.selected or {}, entity_name)
        if not entity_id:
            self.notify("Auto-deploy skipped: record id not available.", severity="warning")
            return
        try:
            await asyncio.to_thread(
                self.client.request, "POST", deploy.route, {"body": {f"{entity_name}Id": entity_id}}
            )
        except httpx.HTTPError as err:
            self.notify(f"Auto-deploy failed: {err}", severity="error", timeout=10)
            return
        self.notify(f"{deploy.route} OK")
        self._refresh_after_action()

    async def _api_get(self, action, params: dict):
        """Execute a GET-style action and return the JSON, or None on error."""
        try:
            response = await asyncio.to_thread(self.client.request, action.method, action.route, params)
            return response.json()
        except httpx.HTTPError as err:
            self.notify(f"API error: {err}", severity="error", timeout=10)
            return None
