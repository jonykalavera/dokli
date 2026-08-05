"""Generic picker: choose one item from a list of candidates."""

from typing import TYPE_CHECKING, Any

from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer, Header, Label

if TYPE_CHECKING:
    from textual.app import ComposeResult


class PickerScreen(Screen):
    """Let the user pick one item from a candidate list.

    Dismisses with the chosen ``value_field`` (or ``None`` on cancel). Await the
    result with ``app.push_screen_wait`` (from a worker) or pass a callback to
    ``app.push_screen``.
    """

    CSS = """
    #picker-list > .selected {
        background: $primary;
        color: $text;
    }
    """

    BINDINGS = [
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
        Binding("down", "cursor_down", "Down", show=False),
        Binding("up", "cursor_up", "Up", show=False),
        Binding("enter", "select", "Select"),
        Binding("escape", "cancel", "Cancel"),
    ]

    def __init__(
        self,
        prompt: str,
        items: list[dict],
        value_field: str,
        label_field: str,
        *args,
        **kwargs,
    ) -> None:
        """Construct the picker screen."""
        super().__init__(*args, **kwargs)
        self.prompt = prompt
        self.items = items
        self.value_field = value_field
        self.label_field = label_field
        self.index = 0

    def compose(self) -> "ComposeResult":
        """Compose the screen."""
        yield Header()
        yield Footer()
        yield Label(self.prompt, classes="title")
        yield VerticalScroll(id="picker-list")

    async def on_mount(self) -> None:
        """On mount, render the candidates."""
        await self._render_items()

    def on_screen_resume(self, event) -> None:
        """On screen resume."""
        self.app.sub_title = self.prompt
        self.run_worker(self._render_items, exclusive=True)  # type: ignore[arg-type]

    async def _render_items(self) -> None:
        """Render the candidate list."""
        container = self.query_one("#picker-list", VerticalScroll)
        await container.remove_children()
        widgets = []
        for n, item in enumerate(self.items):
            label = item.get(self.label_field) or item.get(self.value_field) or "?"
            status = item.get("state") or item.get("status")
            if status:
                label = f"{label} ({status})"
            selected = "selected" if n == self.index else ""
            widgets.append(Label(f"  {label}", classes=selected))
        await container.mount(*widgets)

    def action_cursor_down(self) -> None:
        """Move the cursor down."""
        if self.index < len(self.items) - 1:
            self.index += 1
            self.run_worker(self._render_items, exclusive=True)  # type: ignore[arg-type]

    def action_cursor_up(self) -> None:
        """Move the cursor up."""
        if self.index > 0:
            self.index -= 1
            self.run_worker(self._render_items, exclusive=True)  # type: ignore[arg-type]

    def action_select(self) -> None:
        """Confirm the selection."""
        value: Any = None
        if 0 <= self.index < len(self.items):
            value = self.items[self.index].get(self.value_field)
        self.dismiss(value)

    def action_cancel(self) -> None:
        """Cancel the picker."""
        self.dismiss(None)
