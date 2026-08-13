"""Generic action form (built from an OpenAPI request body schema)."""

from collections.abc import Callable
from typing import TYPE_CHECKING

from textual.binding import Binding
from textual.containers import Horizontal
from textual.screen import Screen
from textual.widgets import Button, Footer, Header

from dokli.config import ConnectionConfig
from dokli.tui.engine import EntityAction, build_form_model
from dokli.tui.forms import Form
from dokli.tui.screens.generic.execute import build_body, confirm_and_run
from dokli.tui.screens.generic.wizard import WizardScreen

if TYPE_CHECKING:
    from textual.app import ComposeResult


class ActionFormScreen(Screen):
    """Render an action form and submit it."""

    BINDINGS = [
        Binding("ctrl+s", "submit", "Submit"),
        Binding("w", "wizard", "Wizard mode"),
        Binding("escape", "cancel", "Cancel"),
    ]

    def __init__(
        self,
        connection: ConnectionConfig,
        action: EntityAction,
        record: dict | None = None,
        on_success: Callable[[], None] | None = None,
        excluded: set[str] | None = None,
        inject: dict | None = None,
        *args,
        **kwargs,
    ) -> None:
        """Construct the action form screen.

        ``excluded`` fields are dropped from the form (e.g. parent-id fields);
        ``inject`` fields are merged into the submitted body (e.g. the parent id
        derived from context).
        """
        super().__init__(*args, **kwargs)
        self.connection = connection
        self.action = action
        self.record = record or {}
        self.on_success = on_success
        self.inject = inject or {}
        model = build_form_model(action.request_schema, name=f"{action.route}Form", excluded=excluded or set())
        prefill = {key: value for key, value in self.record.items() if key in model.model_fields}
        self.form = Form.from_model(model, data=prefill, classes="action-form")

    def compose(self) -> "ComposeResult":
        """Compose the screen."""
        yield Header()
        yield Footer()
        yield self.form
        yield Horizontal(
            Button("Submit", id="submit", variant="primary"),
            Button("Wizard mode", id="wizard"),
            Button("Cancel", id="cancel"),
            classes="actions",
        )

    def on_screen_resume(self, event) -> None:
        """On screen resume."""
        self.app.sub_title = f"{self.connection.name} - {self.action.route}"

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle buttons."""
        if event.button.id == "submit":
            self.action_submit()
        elif event.button.id == "wizard":
            self.action_wizard()
        elif event.button.id == "cancel":
            self.action_cancel()

    def action_submit(self) -> None:
        """Validate and submit the form."""
        if not self.form.validate():
            self.notify("Fix the highlighted fields.", severity="warning")
            return
        data = self.form.cleaned_data or {}
        required = [name for name in self.action.request_schema.get("required", []) if name in self.form.fields]
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
            on_success=self._success,
        )

    def _success(self) -> None:
        """Run the optional success hook, then close the form."""
        if self.on_success is not None:
            self.on_success()
        self.dismiss(None)

    def action_wizard(self) -> None:
        """Open the step-by-step wizard for the same action."""
        self.app.push_screen(WizardScreen(self.connection, self.action, record=self.record, classes="Entities"))

    def action_cancel(self) -> None:
        """Cancel the form."""
        self.dismiss(None)
