"""Result screen: shows the response of a read-only query action."""

import contextlib
from typing import TYPE_CHECKING, Any

import httpx
from rich.text import Text
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer, Header, Input, Label, LoadingIndicator

from dokli.api_client import APIClient
from dokli.config import ConnectionConfig
from dokli.tui.engine import EntityAction, field_label

if TYPE_CHECKING:
    from textual.app import ComposeResult


class ResultScreen(Screen):
    """Show the result of a GET (query) action.

    Press ``r`` to re-fetch the result, ``/`` to search within it: matches are
    highlighted, the position is shown as ``N/M``, and ``n``/``N`` jump to the
    next/previous match. Enter commits the search (blurs the input); escape
    clears it.
    """

    CSS = """
    #search-input { margin: 0 1; }
    #match-status { margin: 0 1; }
    """

    BINDINGS = [
        Binding("escape", "dismiss_screen", "Close"),
        Binding("q", "dismiss_screen", "Close"),
        Binding("enter", "dismiss_screen", "Close"),
        Binding("f5", "refresh", "Refresh"),
        Binding("/", "search", "Search"),
        Binding("n", "next_match", "Next match"),
        Binding("N", "prev_match", "Prev match"),
    ]

    def __init__(
        self,
        connection: ConnectionConfig,
        action: EntityAction,
        data: Any,
        params: dict | None = None,
        *args,
        **kwargs,
    ) -> None:
        """Construct the result screen."""
        super().__init__(*args, **kwargs)
        self.connection = connection
        self.action = action
        self.data = data
        self.params = params or {}
        self._lines: list[str] = []
        self._query = ""
        self._matches: list[int] = []
        self._match_index = 0
        self.search_input = Input(placeholder="Search...", id="search-input")
        self.search_input.display = False
        self.search_input.can_focus = False

    def compose(self) -> "ComposeResult":
        """Compose the screen."""
        yield Header()
        yield Footer()
        yield Label(f"{self.connection.name} · {self.action.route}", classes="title")
        yield self.search_input
        yield VerticalScroll(Label(_render_data(self.data), id="result"), id="result-scroll")
        yield LoadingIndicator(id="result-loading", classes="spinner")
        yield Label("", id="match-status")

    def on_screen_resume(self, event) -> None:
        """On screen resume."""
        self.app.sub_title = f"{self.connection.name} - {self.action.route} result"
        if not self._lines:
            self._lines = _plain_lines(self.data)

    def on_key(self, event) -> None:
        """Intercept enter/escape while the search input is focused."""
        search_input = self.search_input
        if not (search_input.display and self.focused is search_input):
            return
        if event.key == "enter":
            search_input.blur()
            event.stop()
        elif event.key == "escape":
            self._clear_search()
            event.stop()

    # -- refresh -----------------------------------------------------------

    def action_refresh(self) -> None:
        """Re-fetch the result of the action."""
        self.run_worker(self._refresh(), group="action")  # type: ignore[arg-type]

    async def _refresh(self) -> None:
        """Fetch fresh data and re-render (keeping any active search)."""
        self._set_loading(True)
        try:
            response = APIClient(self.connection).request("GET", self.action.route, self.params)
            self.data = response.json()
            self._lines = _plain_lines(self.data)
            self._recompute_matches()
            await self._apply_search()
        except httpx.HTTPError as err:
            self.notify(f"API error: {err}", severity="error", timeout=10)
        finally:
            self._set_loading(False)

    def _set_loading(self, loading: bool) -> None:
        """Show or hide the refresh spinner."""
        with contextlib.suppress(Exception):
            self.query_one("#result-loading", LoadingIndicator).display = loading

    # -- search ------------------------------------------------------------

    def action_search(self) -> None:
        """Open the search input."""
        self.search_input.can_focus = True
        self.search_input.display = True
        self.search_input.focus()

    def action_dismiss_screen(self) -> None:
        """Clear the search if active, otherwise close the screen."""
        search_input = self.search_input
        if search_input.display and self.focused is not search_input:
            self._clear_search()
            return
        self.dismiss(None)

    def action_next_match(self) -> None:
        """Jump to the next match."""
        if self._matches:
            self._match_index = (self._match_index + 1) % len(self._matches)
            self._apply_search_async()

    def action_prev_match(self) -> None:
        """Jump to the previous match."""
        if self._matches:
            self._match_index = (self._match_index - 1) % len(self._matches)
            self._apply_search_async()

    def on_input_changed(self, event) -> None:
        """Live-search as the user types."""
        if event.input.id != "search-input":
            return
        self._query = event.value
        self._match_index = 0
        self._recompute_matches()
        self._apply_search_async()

    def _recompute_matches(self) -> None:
        """Recompute the match lines for the current query."""
        self._matches = [i for i, line in enumerate(self._lines) if self._query.lower() in line.lower()]
        if self._matches:
            self._match_index = min(self._match_index, len(self._matches) - 1)
        else:
            self._match_index = 0

    def _apply_search_async(self) -> None:
        """Schedule a re-render of the highlighted result."""
        self.run_worker(self._apply_search(), exclusive=True, group="search")  # type: ignore[arg-type]

    async def _apply_search(self) -> None:
        """Render the result with the current matches highlighted."""
        container = self.query_one("#result-scroll", VerticalScroll)
        await container.remove_children()
        if not self._query:
            await container.mount(Label(_render_data(self.data), id="result"))
            self._render_status()
            return
        widgets = [Label(self._highlight_line(line, i)) for i, line in enumerate(self._lines)]
        await container.mount(*widgets)
        self._scroll_to_current(container)
        self._render_status()

    def _highlight_line(self, line: str, line_index: int) -> Text:
        """Highlight all occurrences of the query in a line."""
        text = Text()
        query = self._query.lower()
        lower = line.lower()
        start = 0
        while True:
            index = lower.find(query, start)
            if index == -1:
                text.append(line[start:])
                break
            text.append(line[start:index])
            current = line_index == self._matches[self._match_index]
            style = "bold reverse" if current else "#f9e2af"
            text.append(line[index : index + len(query)], style=style)
            start = index + len(query)
        return text

    def _scroll_to_current(self, container: VerticalScroll) -> None:
        """Scroll the current match into view."""
        if not self._matches:
            return
        line_index = self._matches[self._match_index]
        widgets = list(container.children)
        if 0 <= line_index < len(widgets):
            container.scroll_to_widget(widgets[line_index], animate=False)

    def _render_status(self) -> None:
        """Update the match counter label."""
        status = self.query_one("#match-status", Label)
        if not self._query:
            status.update("")
        elif not self._matches:
            status.update("No matches")
        else:
            status.update(f"{self._match_index + 1}/{len(self._matches)} matches")

    def _clear_search(self) -> None:
        """Hide the search input and restore the plain result."""
        search_input = self.search_input
        search_input.display = False
        search_input.value = ""
        self._query = ""
        self._matches = []
        self._match_index = 0
        self._apply_search_async()


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


def _plain_lines(data: Any, indent: int = 0) -> list[str]:
    """Flatten data into plain text lines (logs are split by newline)."""
    pad = "  " * indent
    if isinstance(data, str):
        if "\n" in data:
            return [f"{pad}{line}" for line in data.split("\n")]
        return [f"{pad}{data}"]
    if isinstance(data, dict):
        lines = []
        for key, value in data.items():
            if isinstance(value, dict | list):
                lines.append(f"{pad}{field_label(key)}:")
                lines.extend(_plain_lines(value, indent + 1))
            else:
                lines.append(f"{pad}{field_label(key)}: {value}")
        return lines
    if isinstance(data, list):
        if not data:
            return [f"{pad}(empty)"]
        lines = []
        for item in data:
            if isinstance(item, dict | list):
                lines.extend(_plain_lines(item, indent))
            else:
                lines.append(f"{pad}- {item}")
        return lines
    return [f"{pad}{data}"]
