"""Project detail screen."""

from typing import TYPE_CHECKING

from textual import events
from textual.binding import Binding
from textual.css.query import NoMatches
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Footer, Header, Label, ListItem, ListView

from dokli.models.project import Project
from dokli.models.redis import RedisService
from dokli.tui.widgets.list_item import AddItem
from dokli.tui.widgets.main_menu import MainMenu

if TYPE_CHECKING:
    from textual.app import ComposeResult


class RedisServiceItem(ListItem):
    """Redis service item."""

    ICON = ""

    service: RedisService

    def __init__(self, service: RedisService, *args, **kwargs) -> None:
        """Construct a redis service item."""
        super().__init__(*args, **kwargs)
        self.service = service

    def compose(self) -> "ComposeResult":
        """Compose the widget."""
        yield Label(self.ICON, id="icon")
        yield Label(self.service.name, id="name", classes="title")
        yield Label(self.service.appName, id="appName")
        yield Label(f"Created {self.service.time_since_created}", id="time_since_created")


class ProjectDetailScreen(Screen):
    """Project detail screen."""

    model = Project
    instance: reactive[Project | None] = reactive(None)

    BINDINGS = [
        Binding("e", "edit", "Edit"),
        Binding("d", "delete", "Delete"),
    ]

    def __init__(self, instance: Project, *args, **kwargs) -> None:
        """Construct a project detail screen."""
        super().__init__(*args, **kwargs)
        self.instance = instance

    def on_screen_resume(self, event: events.ScreenResume) -> None:
        """On screen resume."""
        self.app.sub_title = f"{self.app.connection.name}  Projects  {self.instance.name}"
        try:
            list_view = self.query_one(ListView)
            list_view.focus()
        except NoMatches:
            pass

    def compose(self) -> "ComposeResult":
        """Compose the widget."""
        yield Header()
        yield Footer()
        yield MainMenu(active_screen="Projects")
        yield Label(self.instance.name if self.instance else "", id="name", classes="title")
        yield Label(self.instance.description if self.instance else "", id="description", classes="subtitle")
        yield ListView(
            *(RedisServiceItem(RedisService.model_validate(service)) for service in self.instance.services),
            AddItem(id="__add__", item_name="service"),
            id="services",
        )

    def watch_instance(self, old_value, new_value) -> None:
        """Watch instance changes."""
        try:
            title = self.query_one("Label#title")
            description = self.query_one("Label#description")
        except NoMatches:
            return
        if new_value:
            assert isinstance(title, Label)
            title.renderable = new_value.name
            assert isinstance(description, Label)
            description.renderable = new_value.description
