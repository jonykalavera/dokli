"""Generic action form (built from an OpenAPI request body schema)."""

from typing import TYPE_CHECKING

import httpx
from pydantic import SecretBytes, SecretStr
from textual import log
from textual.binding import Binding
from textual.message import Message
from textual.screen import Screen
from textual.widgets import Button, Footer, Header

from dokli.api_client import APIClient
from dokli.config import ConnectionConfig
from dokli.tui.engine import EntityAction, build_form_model
from dokli.tui.forms import Form

if TYPE_CHECKING:
    from textual.app import ComposeResult


class ActionFormScreen(Screen):
    """Render an action form and submit it."""

    BINDINGS = [
        Binding("ctrl+s", "submit", "Submit"),
        Binding("escape", "cancel", "Cancel"),
    ]

    class Submitted(Message):
        """The form was submitted successfully."""

        def __init__(self, route: str, response: httpx.Response) -> None:
            """Construct the message."""
            super().__init__()
            self.route = route
            self.response = response

    def __init__(
        self,
        connection: ConnectionConfig,
        action: EntityAction,
        record: dict | None = None,
        *args,
        **kwargs,
    ) -> None:
        """Construct the action form screen."""
        super().__init__(*args, **kwargs)
        self.connection = connection
        self.action = action
        self.record = record or {}
        model = build_form_model(action.request_schema, name=f"{action.route}Form")
        prefill = {key: value for key, value in self.record.items() if key in model.model_fields}
        self.form = Form.from_model(model, data=prefill, classes="action-form")

    def compose(self) -> "ComposeResult":
        """Compose the screen."""
        yield Header()
        yield Footer()
        yield self.form
        yield Button("Submit", id="submit", variant="primary")
        yield Button("Cancel", id="cancel")

    def on_screen_resume(self, event) -> None:
        """On screen resume."""
        self.app.sub_title = f"{self.connection.name} - {self.action.route}"

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle buttons."""
        if event.button.id == "submit":
            self.action_submit()
        elif event.button.id == "cancel":
            self.action_cancel()

    def action_submit(self) -> None:
        """Validate and submit the form."""
        if not self.form.validate():
            self.notify("Fix the highlighted fields.", severity="warning")
            return
        data = self.form.cleaned_data or {}
        required = self.action.request_schema.get("required", [])
        missing = [name for name in required if not data.get(name)]
        if missing:
            self.notify(f"Missing required: {', '.join(missing)}", severity="error", timeout=10)
            return
        body = {}
        for key, raw_value in data.items():
            if raw_value in ("", None):
                continue
            value = (
                raw_value.get_secret_value()
                if isinstance(raw_value, SecretStr | SecretBytes)
                else raw_value
            )
            body[key] = value
        self._execute(body)

    def _execute(self, body: dict) -> None:
        log("submitting", self.action.route, body)
        client = APIClient(self.connection)
        try:
            response = client.request(self.action.method, self.action.route, {"body": body})
        except httpx.HTTPError as err:
            self.notify(f"API error: {err}", severity="error", timeout=10)
            log("api error", err)
            return
        self.post_message(self.Submitted(self.action.route, response))
        self.notify(f"{self.action.route} OK")
        self.dismiss(None)

    def action_cancel(self) -> None:
        """Cancel the form."""
        self.dismiss(None)
