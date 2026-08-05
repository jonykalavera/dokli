"""Generic help screen: lists the keybindings of the app and active screen."""

from typing import TYPE_CHECKING

from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer, Header, Label

if TYPE_CHECKING:
    from textual.app import ComposeResult


class HelpScreen(Screen):
    """Show the keybindings for the app and the screen that requested help."""

    BINDINGS = [
        Binding("escape", "close", "Close"),
        Binding("q", "close", "Close"),
    ]

    def compose(self) -> "ComposeResult":
        """Compose the screen."""
        yield Header()
        yield Footer()
        yield Label("Keybindings", classes="title")
        yield VerticalScroll(id="help-scroll")

    def on_screen_resume(self, event) -> None:
        """On screen resume."""
        self.app.sub_title = "Help"
        self.run_worker(self._render_items, exclusive=True)  # type: ignore[arg-type]
    async def _render_items(self) -> None:
        """Render the bindings of the app and the previous screen."""
        container = self.query_one("#help-scroll", VerticalScroll)
        await container.remove_children()
        widgets = []
        sources = []
        previous = self.app.screen_stack[-2] if len(self.app.screen_stack) >= 2 else None
        if previous is not None:
            sources.append(
                (type(previous).__name__, previous.BINDINGS, getattr(previous, "contextual_bindings", None))
            )
        sources.append(("App", self.app.BINDINGS, None))
        for title, bindings, contextual in sources:
            entries = _merge_entries(_binding_entries(bindings), contextual() if contextual else None)
            if not entries:
                continue
            widgets.append(Label(title, classes="section"))
            for key, description in entries:
                widgets.append(Label(f"  [b]{key}[/b]  {description}"))
        await container.mount(*widgets)

    def action_close(self) -> None:
        """Close the help screen."""
        self.dismiss(None)


def _merge_entries(
    default: list[tuple[str, str]], contextual: list[tuple[str, str]] | None
) -> list[tuple[str, str]]:
    """Combine default and contextual bindings, default winning on collisions."""
    merged: dict[str, str] = {}
    for entries in (default, contextual or []):
        for key, description in entries:
            merged.setdefault(key, description)
    return list(merged.items())


def _binding_entries(bindings) -> list[tuple[str, str]]:
    """Normalize BINDINGS (Binding or tuple entries) into (key, description)."""
    entries = []
    for binding in bindings:
        if isinstance(binding, Binding):
            key, description, show = binding.key, binding.description, binding.show
        else:
            parts = list(binding)
            key = str(parts[0])
            description = str(parts[2]) if len(parts) > 2 else ""
            show = True
        if show and description:
            entries.append((key, description))
    return entries