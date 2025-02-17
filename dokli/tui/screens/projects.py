"""Projects screen."""

from typing import TYPE_CHECKING

from textual import events, log
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import (
    Footer,
    Header,
    Label,
    ListItem,
    ListView,
    LoadingIndicator,
)

from dokli.commands import HTTPError, Response, run_command
from dokli.config import ConnectionConfig
from dokli.formatting import Format, format_response
from dokli.models.project import Project
from dokli.tui.screens.project import ProjectDetailScreen
from dokli.tui.widgets.list_item import AddItem
from dokli.tui.widgets.main_menu import MainMenu

if TYPE_CHECKING:
    from textual.app import ComposeResult


class ProjectListItem(ListItem):
    """A project widget."""

    ICON = ""
    SERVICE_ICONS = {
        "python": "",
        "docker": "",
        "redis": "",
        "mysql": "",
        "postgres": "",
        "mariadb": "",
        "compose": "",
        "mongo": "",
        "applications": "",
    }

    def __init__(self, project: Project, *args, **kwargs) -> None:
        """Construct a project widget."""
        super().__init__(*args, **kwargs)
        self.project = project

    def _get_markers(self) -> str:
        MARKER_FIELDS = {"applications", "mariadb", "mongo", "mysql", "postgres", "redis", "compose"}
        markers = []
        num_services = 0
        for marker in MARKER_FIELDS:
            num = len(getattr(self.project, marker, []))
            markers.append(f"{self.SERVICE_ICONS[marker]} {num}")
            num_services += num
        return f"{num_services} services" + ((": " + " ".join(markers)) if markers else "")

    def compose(self) -> "ComposeResult":
        """Compose the widget."""
        yield Label(self.ICON, id="icon")
        yield Label(self.project.name, id="name", classes="title")
        yield Label(self.project.description or "", id="description")
        yield Label(self._get_markers(), id="markers")
        yield Label("Created " + self.project.time_since_created, id="time_since_created")


class ProjectsScreen(Screen):
    """Projects screen."""

    BINDINGS = [
        Binding("r", "refresh_projects", "Refresh"),
    ]

    def compose(self) -> "ComposeResult":
        """Create child widgets for the app."""
        yield Header()
        yield Footer()
        yield MainMenu(active_screen="Projects")
        yield ListView()
        yield LoadingIndicator(id="loading")

    def on_screen_resume(self, event: events.ScreenResume) -> None:
        """On mount."""
        assert hasattr(self.app, "connection")
        self.app.sub_title = f"{self.app.connection.name} - Projects"
        self.action_refresh_projects()

    def action_refresh_projects(self) -> None:
        """Refresh projects list."""
        assert hasattr(self.app, "connection")
        self.run_worker(self._update_projects(self.app.connection), exclusive=True)

    async def _update_projects(self, connection: ConnectionConfig) -> None:
        """Update the weather for the given city."""
        loading = self.query_one(LoadingIndicator)
        loading.classes = ""

        # Query the network API
        response = run_command(self.app.connection, method="GET", route="project.all")
        match response:
            case Response():
                await self._load_response(response)
            case HTTPError():
                self.notify(
                    f"API error: {response!r}!",
                    severity="error",
                    timeout=10,
                )
                log("api error", response, self.app.connection)
                loading.classes = "hidden"

    async def _load_response(self, response: Response) -> None:
        list_view = self.query_one(ListView)
        loading = self.query_one(LoadingIndicator)
        data = format_response(response, format=Format.python)
        await list_view.clear()
        list_view.extend(
            [
                *(ProjectListItem(Project.model_validate(item)) for item in data),
                AddItem(id="__add__", item_name="project"),
            ]
        )
        loading.classes = "hidden"
        list_view.focus()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """On list view selected."""
        match type(event.item):
            case ProjectListItem():
                self.app.push_screen(ProjectDetailScreen(event.item.project, classes="Projects"))
            case AddItem():
                self.app.push_screen("AddProject")
