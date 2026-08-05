"""Result screen: shows the response of a read-only query action."""

from typing import TYPE_CHECKING, Any

from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer, Header, Label

from dokli.config import ConnectionConfig
from dokli.tui.engine import EntityAction, field_label

if TYPE_CHECKING:
    from textual.app import ComposeResult


class ResultScreen(Screen):
    """Show the result of a GET (query) action."""

    BINDINGS = [
        Binding("escape", "dismiss_screen", "Close"),
        Binding("q", "dismiss_screen", "Close"),
        Binding("enter", "dismiss_screen", "Close"),
    ]

    def __init__(
        self,
        connection: ConnectionConfig,
        action: EntityAction,
        data: Any,
        *args,
        **kwargs,
    ) -> None:
        """Construct the result screen."""
        super().__init__(*args, **kwargs)
        self.connection = connection
        self.action = action
        self.data = data

    def compose(self) -> "ComposeResult":
        """Compose the screen."""
        yield Header()
        yield Footer()
        yield Label(f"{self.connection.name} · {self.action.route}", classes="title")
        yield VerticalScroll(Label(_render_data(self.data), id="result"), id="result-scroll")

    def on_screen_resume(self, event) -> None:
        """On screen resume."""
        self.app.sub_title = f"{self.connection.name} - {self.action.route} result"

    def action_dismiss_screen(self) -> None:
        """Close the result screen."""
        self.dismiss(None)


def _render_data(data: Any, indent: int = 0) -> str:
    """Render arbitrary response data as rich markup text."""
    pad = "  " * indent
    if isinstance(data, dict):
        lines = []
        for key, value in data.items():
            if isinstance(value, dict | list):
                lines.append(f"{pad}{field_label(key)}:")
                lines.append(_render_data(value, indent + 1))
            else:
                lines.append(f"{pad}[b]{field_label(key)}:[/b] {value}")
        return "\n".join(lines)
    if isinstance(data, list):
        if not data:
            return f"{pad}(empty)"
        lines = []
        for item in data:
            if isinstance(item, dict | list):
                lines.append(_render_data(item, indent))
            else:
                lines.append(f"{pad}- {item}")
        return "\n".join(lines)
    return f"{pad}{data}"
