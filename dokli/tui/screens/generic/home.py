"""Generic entity picker (home screen)."""

from typing import TYPE_CHECKING

from textual.binding import Binding
from textual.css.query import NoMatches
from textual.screen import Screen
from textual.widgets import Footer, Header, Input, Label, ListItem, ListView

from dokli.config import ConnectionConfig
from dokli.tui.engine.spec import CORE_ENTITIES, EntityRegistry
from dokli.tui.screens.generic.entity_list import EntityListScreen

if TYPE_CHECKING:
    from textual.app import ComposeResult


class EntityItem(ListItem):
    """An entity in the home list."""

    def __init__(self, name: str, core: bool, *args, **kwargs) -> None:
        """Construct an entity item."""
        super().__init__(*args, **kwargs)
        self.entity_name = name
        self.core = core

    def compose(self) -> "ComposeResult":
        """Compose the widget."""
        yield Label(f"{'●' if self.core else '○'} {self.entity_name}", id="name", classes="title")
        yield Label("core" if self.core else "discovered", id="meta")


class HomeScreen(Screen):
    """Entity picker screen."""

    BINDINGS = [
        Binding("escape", "cancel", "Back"),
        Binding("tab", "focus_list", "Focus list"),
    ]

    def __init__(
        self,
        connection: ConnectionConfig,
        registry: EntityRegistry,
        *args,
        **kwargs,
    ) -> None:
        """Construct the home screen."""
        super().__init__(*args, **kwargs)
        self.connection = connection
        self.registry = registry

    def compose(self) -> "ComposeResult":
        """Compose the screen."""
        yield Header()
        yield Footer()
        yield Input(placeholder="Search entities...", id="search")
        yield ListView(id="entities")

    def on_screen_resume(self, event) -> None:
        """On screen resume."""
        self.app.sub_title = f"{self.connection.name} - Entities"
        self._refresh()

    def on_input_changed(self, event) -> None:
        """Filter the entity list as the user types."""
        self._refresh()

    def action_focus_list(self) -> None:
        """Focus the entity list."""
        self.query_one(ListView).focus()

    def _refresh(self) -> None:
        self.run_worker(self._refresh_entities(), exclusive=True)

    async def _refresh_entities(self) -> None:
        query = ""
        try:
            search = self.query_one("#search", Input)
            query = search.value.lower()
        except NoMatches:
            pass
        names = self.registry.names()
        ordered = [name for name in CORE_ENTITIES if name in names] + [
            name for name in names if name not in CORE_ENTITIES
        ]
        filtered = [name for name in ordered if query in name.lower()]
        list_view = self.query_one("#entities", ListView)
        await list_view.clear()
        list_view.extend(
            [
                EntityItem(name, name in CORE_ENTITIES, id=f"entity__{name}")
                for name in filtered
            ]
        )
        list_view.focus()

    def on_list_view_selected(self, event) -> None:
        """Open the selected entity."""
        if isinstance(event.item, EntityItem):
            self.app.push_screen(
                EntityListScreen(self.connection, self.registry, event.item.entity_name, classes="Entities")
            )
