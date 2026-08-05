"""Generic entity list (via ``entity.all``)."""

from typing import TYPE_CHECKING

from textual import log
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import Footer, Header, Label, ListItem, ListView, LoadingIndicator

from dokli.commands import HTTPError, Response, run_command
from dokli.config import ConnectionConfig
from dokli.tui.engine import EntityRegistry, record_subtitle, record_title
from dokli.tui.screens.generic.record import RecordScreen

if TYPE_CHECKING:
    from textual.app import ComposeResult


class RecordItem(ListItem):
    """A record in the entity list."""

    def __init__(self, record: dict, *args, **kwargs) -> None:
        """Construct a record item."""
        super().__init__(*args, **kwargs)
        self.record = record

    def compose(self) -> "ComposeResult":
        """Compose the widget."""
        yield Label(record_title(self.record), id="name", classes="title")
        subtitle = record_subtitle(self.record)
        if subtitle:
            yield Label(subtitle, id="subtitle")


class EntityListScreen(Screen):
    """List records of an entity."""

    BINDINGS = [
        Binding("r", "refresh", "Refresh"),
        Binding("escape", "cancel", "Back"),
    ]

    def __init__(
        self,
        connection: ConnectionConfig,
        registry: EntityRegistry,
        entity_name: str,
        *args,
        **kwargs,
    ) -> None:
        """Construct the entity list screen."""
        super().__init__(*args, **kwargs)
        self.connection = connection
        self.registry = registry
        self.entity_name = entity_name

    def compose(self) -> "ComposeResult":
        """Compose the screen."""
        yield Header()
        yield Footer()
        yield ListView(id="records")
        yield LoadingIndicator(id="loading")

    def on_screen_resume(self, event) -> None:
        """On screen resume."""
        self.app.sub_title = f"{self.connection.name} - {self.entity_name}"
        self._refresh()

    def action_refresh(self) -> None:
        """Refresh the record list."""
        self._refresh()

    def _refresh(self) -> None:
        entity = self.registry.get(self.entity_name)
        action = entity.get("all") if entity else None
        if action is None:
            self.notify(f"'{self.entity_name}' has no 'all' action.", severity="warning")
            return
        self.run_worker(self._load(action.route), exclusive=True)

    async def _load(self, route: str) -> None:
        loading = self.query_one(LoadingIndicator)
        loading.classes = ""
        response = run_command(self.connection, method="GET", route=route)
        match response:
            case Response():
                data = response.json()
                records = data if isinstance(data, list) else data.get("items", [])
                await self._populate(records)
            case HTTPError():
                self.notify(f"API error: {response!r}", severity="error", timeout=10)
                log("api error", response)
        loading.classes = "hidden"

    async def _populate(self, records: list[dict]) -> None:
        list_view = self.query_one(ListView)
        await list_view.clear()
        list_view.extend([RecordItem(record, id=f"record__{n}") for n, record in enumerate(records)])
        list_view.focus()

    def on_list_view_selected(self, event) -> None:
        """Open the selected record."""
        if isinstance(event.item, RecordItem):
            self.app.push_screen(
                RecordScreen(self.connection, self.registry, self.entity_name, event.item.record, classes="Entities")
            )
