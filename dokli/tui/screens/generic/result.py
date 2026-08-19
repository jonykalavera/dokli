"""Result screen: shows the response of a read-only query action."""

import asyncio
import contextlib
import re
from collections import deque
from datetime import datetime
from typing import TYPE_CHECKING, Any, cast

import httpx
from rich.text import Text
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer, Header, Input, Label, LoadingIndicator

from dokli.api_client import APIClient
from dokli.config import ConnectionConfig
from dokli.tui.engine import EntityAction, field_label
from dokli.wss import DEPLOYMENT_LOGS_ENDPOINT, LOGS_ENDPOINT, iter_lines

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from dokli.tui.app import DokliApp

#: Lines kept in the follow-mode buffer (bounded memory).
MAX_LOG_LINES = 5000
#: Leading docker timestamp (``2026-08-13T23:21:05.610653897Z`` or ``...Z ``).
_TIMESTAMP_RE = re.compile(r"^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z) ")


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
    #result { width: 100%; }
    """

    BINDINGS = [
        Binding("escape", "dismiss_screen", "Close"),
        Binding("q", "dismiss_screen", "Close"),
        Binding("enter", "dismiss_screen", "Close"),
        Binding("f5", "refresh", "Refresh"),
        Binding("/", "search", "Search"),
        Binding("n", "next_match", "Next match"),
        Binding("N", "prev_match", "Prev match"),
        Binding("f", "toggle_follow", "Follow"),
        Binding("end", "tail", "Tail"),
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
        self._is_logs = action.verb == "readLogs"
        self._follow = self._is_logs
        self._auto_scroll = self._is_logs
        self._last_ts: datetime | None = None
        self._follow_worker = None
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
            if self._is_logs:
                self._lines = [line for line in self._lines if line]
            self._last_ts = _latest_timestamp(self._lines)
            if self._is_logs:
                self._rerender_logs()
                if self._follow:
                    self.query_one("#result-scroll", VerticalScroll).scroll_end(animate=False)
        self._render_status()
        if self._follow:
            self._start_follow()

    def on_screen_suspend(self, event) -> None:
        """Stop polling while another screen is on top."""
        if self._follow_worker is not None:
            self._follow_worker.cancel()
            self._follow_worker = None

    def _start_follow(self) -> None:
        """Start the follow-mode loop: WebSocket stream when available, else polling."""
        if self._follow_worker is not None and not self._follow_worker.is_cancelled:
            return
        if self._log_stream_spec() is not None:
            self._follow_worker = self.run_worker(  # type: ignore[arg-type]
                self._follow_ws(), group="follow"
            )
        else:
            self._follow_worker = self.run_worker(  # type: ignore[arg-type]
                self._poll_follow(), group="follow"
            )

    def _log_stream_spec(self) -> dict | None:
        """The WebSocket stream spec for this logs result, if any.

        Container logs stream via ``containerId`` (docker/compose readLogs); a
        deployment streams via its ``logPath`` (threaded from the browser).
        Returns ``None`` otherwise, so follow-mode falls back to polling.
        """
        if not self._is_logs:
            return None
        if self.params.get("containerId"):
            return {
                "endpoint": LOGS_ENDPOINT,
                "params": {
                    key: self.params[key]
                    for key in ("containerId", "serverId", "serviceId", "runType")
                    if self.params.get(key)
                },
            }
        if self.params.get("logPath"):
            stream_params = {"logPath": self.params["logPath"]}
            if self.params.get("serverId"):
                stream_params["serverId"] = self.params["serverId"]
            return {"endpoint": DEPLOYMENT_LOGS_ENDPOINT, "params": stream_params}
        return None

    async def _follow_ws(self) -> None:
        """Stream log lines over WebSocket; fall back to polling on failure.

        While connected the stream is the source of truth: the buffer is rebuilt
        from it (the server sends the tail history, then follows). Any
        connection/auth error switches to the polling API.
        """
        spec = self._log_stream_spec()
        if spec is None:
            await self._poll_follow()
            return
        params = dict(spec["params"])
        if spec["endpoint"] == LOGS_ENDPOINT:
            params["tail"] = cast("DokliApp", self.app).config.tui.logs_tail_lines
        self._lines = []
        self._last_ts = None
        try:
            async for raw in iter_lines(self.connection, spec["endpoint"], params):
                line = raw.rstrip("\r")
                if not line:
                    continue
                self._merge_log_lines([line])
                if self._query:
                    continue
                self._rerender_logs()
                self._pin_to_tail()
                self._render_status()
        except Exception:
            self.notify("Live logs unavailable; falling back to polling.", severity="warning", timeout=5)
            self._lines = [line for line in _plain_lines(self.data) if line]
            self._last_ts = _latest_timestamp(self._lines)
            self._rerender_logs()
            await self._poll_follow()

    async def _poll_follow(self) -> None:
        """Periodically fetch newer log lines and append them to the view."""
        interval = cast("DokliApp", self.app).config.tui.logs_interval_seconds
        while True:
            await asyncio.sleep(interval)
            await self._fetch_follow()

    def _pin_to_tail(self) -> None:
        """Pin to the tail while auto-scroll is active, else mark the view paused."""
        container = self.query_one("#result-scroll", VerticalScroll)
        if self._auto_scroll and container.scroll_y >= container.max_scroll_y - 1:
            container.scroll_end(animate=False)
        elif self._auto_scroll:
            self._auto_scroll = False

    async def _fetch_follow(self) -> None:
        """Fetch one batch of log lines, merge, and pin to the tail if wanted."""
        params = {**self.params, "tail": cast("DokliApp", self.app).config.tui.logs_tail_lines}
        try:
            response = await asyncio.to_thread(
                lambda: APIClient(self.connection).request("GET", self.action.route, params)
            )
        except httpx.HTTPError as err:
            self.notify(f"API error: {err}", severity="error", timeout=10)
            return
        new_lines = _plain_lines(response.json())
        if self._is_logs:
            new_lines = [line for line in new_lines if line]
        self._merge_log_lines(new_lines)
        if self._query:
            return
        self._rerender_logs()
        self._pin_to_tail()
        self._render_status()

    def _merge_log_lines(self, incoming: list[str]) -> None:
        """Append incoming log lines to the buffer, de-duplicating by timestamp.

        Lines without a docker timestamp (e.g. deployment build logs) cannot be
        de-duplicated per-line, so the batch is matched against the buffer tail
        first: a re-fetched tail that is already present is skipped entirely.
        """
        incoming = [line for line in incoming if line]
        if not self._lines:
            self._lines = incoming[:MAX_LOG_LINES]
            self._last_ts = _latest_timestamp(self._lines)
            return
        buffer = deque(self._lines)
        last_ts = self._last_ts or _latest_timestamp(self._lines)
        skip = _tail_overlap(list(buffer), incoming)
        for line in incoming[skip:]:
            ts = _timestamp_of(line)
            if ts is not None:
                if last_ts is not None and ts <= last_ts:
                    continue
                last_ts = ts
                buffer.append(line)
                continue
            if line == buffer[-1]:
                continue
            buffer.append(line)
        self._lines = list(buffer)[-MAX_LOG_LINES:]
        self._last_ts = last_ts

    def _rerender_logs(self) -> None:
        """Re-render the log lines with dimmed timestamps."""
        label = self.query_one("#result", Label)
        text = Text()
        for i, line in enumerate(self._lines):
            if i:
                text.append("\n")
            text.append(_log_line_text(line))
        label.update(text)

    def action_toggle_follow(self) -> None:
        """Toggle follow mode on/off."""
        self._follow = not self._follow
        if self._follow:
            self._auto_scroll = True
            self._start_follow()
            self.query_one("#result-scroll", VerticalScroll).scroll_end(animate=False)
        elif self._follow_worker is not None:
            self._follow_worker.cancel()
            self._follow_worker = None
        self._render_status()

    def action_tail(self) -> None:
        """Scroll to the tail and resume auto-scroll."""
        self._auto_scroll = True
        self.query_one("#result-scroll", VerticalScroll).scroll_end(animate=False)
        self._render_status()

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
            response = await asyncio.to_thread(
                lambda: APIClient(self.connection).request("GET", self.action.route, self.params)
            )
            self.data = response.json()
            self._lines = _plain_lines(self.data)
            if self._is_logs:
                self._lines = [line for line in self._lines if line]
            self._last_ts = _latest_timestamp(self._lines)
            self._recompute_matches()
            await self._apply_search()
            if not self._query:
                self.query_one("#result-scroll", VerticalScroll).scroll_home(animate=False)
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
        """Render the result with the current matches highlighted.

        A single persistent ``#result`` Label is updated in place — the scroll
        container never re-mounts children, keeping its scrollbar stable.
        """
        self._recompute_matches()
        label = self.query_one("#result", Label)
        if not self._query:
            if self._is_logs:
                self._rerender_logs()
            else:
                label.update(_render_data(self.data))
            self._render_status()
            return
        text = Text()
        for i, line in enumerate(self._lines):
            if i:
                text.append("\n")
            text.append(self._highlight_line(line, i))
        label.update(text)
        self._scroll_to_current()
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

    def _scroll_to_current(self) -> None:
        """Scroll the current match into view."""
        if not self._matches:
            return
        container = self.query_one("#result-scroll", VerticalScroll)
        line_index = self._matches[self._match_index]
        container.scroll_to(y=_display_row(self._lines, line_index, container.size.width), animate=False)

    def _render_status(self) -> None:
        """Update the match counter and follow-mode indicator."""
        status = self.query_one("#match-status", Label)
        parts: list[str] = []
        if self._is_logs:
            if self._follow:
                parts.append("[bold green]●[/] live" if self._auto_scroll else "[dim]⏸[/] paused")
            else:
                parts.append("[dim]○[/] follow off")
        if self._query:
            if not self._matches:
                parts.append("No matches")
            else:
                parts.append(f"{self._match_index + 1}/{len(self._matches)} matches")
        status.update("   ".join(parts))

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


def _timestamp_of(line: str) -> datetime | None:
    """The parsed leading docker timestamp of a log line, if any."""
    match = _TIMESTAMP_RE.match(line)
    if match is None:
        return None
    try:
        return datetime.fromisoformat(match.group(1).replace("Z", "+00:00"))
    except ValueError:
        return None


def _tail_overlap(buffer: list[str], incoming: list[str]) -> int:
    """How many leading ``incoming`` lines are already the buffer's tail.

    Follow-mode polls re-fetch the last ``logs_tail_lines`` lines; the largest
    ``k`` such that ``incoming[:k] == buffer[-k:]`` are duplicates already on
    screen (handles log lines without docker timestamps, e.g. deployments).
    """
    for k in range(min(len(buffer), len(incoming)), 0, -1):
        if incoming[:k] == buffer[-k:]:
            return k
    return 0


def _display_row(lines: list[str], index: int, width: int) -> int:
    """The rendered row of ``lines[index]`` when wrapped at ``width`` columns."""
    width = max(1, width)
    rows = 0
    for line in lines[:index]:
        rows += max(1, (len(line) + width - 1) // width)
    return rows


def _latest_timestamp(lines: list[str]) -> datetime | None:
    """The newest docker timestamp across a list of log lines."""
    latest: datetime | None = None
    for line in lines:
        ts = _timestamp_of(line)
        if ts is not None and (latest is None or ts > latest):
            latest = ts
    return latest


def _log_line_text(line: str) -> Text:
    """A log line with its leading docker timestamp dimmed, in local time."""
    match = _TIMESTAMP_RE.match(line)
    if match is None:
        return Text(line)
    text = Text()
    ts = _timestamp_of(line)
    stamp = ts.astimezone().strftime("%Y-%m-%d %H:%M:%S") if ts else match.group(1)
    text.append(f"{stamp} ", style="dim")
    text.append(line[match.end() :])
    return text


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
