"""Step-by-step wizard form (one field at a time)."""

from typing import TYPE_CHECKING

from textual.binding import Binding
from textual.containers import Container, Horizontal
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Label

from dokli.config import ConnectionConfig
from dokli.tui.engine import EntityAction, build_form_model
from dokli.tui.forms import FormControl
from dokli.tui.screens.generic.execute import build_body, confirm_and_run

if TYPE_CHECKING:
    from textual.app import ComposeResult


class WizardScreen(Screen):
    """Prompt each field of an action form in sequence."""

    BINDINGS = [
        Binding("ctrl+n", "next", "Next"),
        Binding("ctrl+p", "back", "Back"),
        Binding("escape", "cancel", "Cancel"),
    ]

    def __init__(
        self,
        connection: ConnectionConfig,
        action: EntityAction,
        record: dict | None = None,
        excluded: set[str] | None = None,
        inject: dict | None = None,
        *args,
        **kwargs,
    ) -> None:
        """Construct the wizard screen."""
        super().__init__(*args, **kwargs)
        self.connection = connection
        self.action = action
        self.record = record or {}
        self.inject = inject or {}
        self.model = build_form_model(action.request_schema, name=f"{action.route}Wizard", excluded=excluded or set())
        self.fields = list(self.model.model_fields.items())
        self.controls = {
            name: FormControl.from_field(name, field, value=self.record.get(name)) for name, field in self.fields
        }
        self.index = 0

    def compose(self) -> "ComposeResult":
        """Compose the screen."""
        yield Header()
        yield Footer()
        yield Label("", id="prompt", classes="title")
        yield Container(id="control")
        yield Horizontal(
            Button("Back", id="back"),
            Button("Next", id="next", variant="primary"),
            Button("Cancel", id="cancel"),
            classes="actions",
        )

    def on_screen_resume(self, event) -> None:
        """On screen resume."""
        self.app.sub_title = f"{self.connection.name} - {self.action.route} (wizard)"
        self._show()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle buttons."""
        if event.button.id == "back":
            self.action_back()
        elif event.button.id == "next":
            self.action_next()
        elif event.button.id == "cancel":
            self.action_cancel()

    def _show(self) -> None:
        name, field = self.fields[self.index]
        control = self.controls[name]
        container = self.query_one("#control", Container)
        container.remove_children()
        container.mount(control)
        self.query_one("#prompt", Label).update(f"({self.index + 1}/{len(self.fields)}) {field.title or name}")
        control.focus()

    def action_next(self) -> None:
        """Advance to the next field, or finish on the last one."""
        if self.index < len(self.fields) - 1:
            self.index += 1
            self._show()
        else:
            self._finish()

    def action_back(self) -> None:
        """Go back to the previous field."""
        if self.index > 0:
            self.index -= 1
            self._show()

    def action_cancel(self) -> None:
        """Cancel the wizard."""
        self.dismiss(None)

    def _finish(self) -> None:
        data = {name: self.controls[name].get_data() for name, _ in self.fields}
        required = [name for name in self.action.request_schema.get("required", []) if name in self.controls]
        missing = [name for name in required if not data.get(name)]
        if missing:
            self.notify(f"Missing required: {', '.join(missing)}", severity="error", timeout=10)
            return
        body = build_body(self.action, data)
        confirm_and_run(
            self,
            self.connection,
            self.action,
            {**self.inject, **body},
            on_success=lambda: self.dismiss(None),
        )
