"""Generic action form (built from an OpenAPI request body schema)."""

import asyncio
from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from textual.binding import Binding
from textual.containers import Horizontal
from textual.screen import Screen
from textual.widgets import Button, Footer, Header

from dokli.config import ConnectionConfig
from dokli.tui.engine import EntityAction, build_form_model
from dokli.tui.engine.conditionals import conditional_switches
from dokli.tui.engine.fk import load_fk_candidates, resolve_service_source
from dokli.tui.forms import FkSelectControl, Form
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
        context: dict | None = None,
        *args,
        **kwargs,
    ) -> None:
        """Construct the action form screen.

        ``excluded`` fields are dropped from the form (e.g. parent-id fields);
        ``inject`` fields are merged into the submitted body (e.g. the parent id
        derived from context); ``context`` holds navigation context used to
        resolve FK source params (e.g. the current ``projectId``).
        """
        super().__init__(*args, **kwargs)
        self.connection = connection
        self.action = action
        self.record = record or {}
        self.on_success = on_success
        self.excluded = excluded or set()
        self.inject = inject or {}
        self.context = context or {}
        self._fk_cache: dict = {}
        model = build_form_model(action.request_schema, name=f"{action.route}Form", excluded=self.excluded)
        prefill = {key: value for key, value in self.record.items() if key in model.model_fields}
        entity = self.action.route.split(".")[0]
        self.form = Form.from_model(
            model,
            data=prefill,
            classes="action-form",
            conditional=conditional_switches(entity),
        )
        for control in self.form.fields.values():
            if isinstance(control, FkSelectControl):
                control.fetch = self._fk_fetcher(control)

    def _fk_fetcher(self, control: FkSelectControl) -> Callable[[], Any]:
        """A fetcher that loads the FK control's candidates off the event loop."""
        source = control.fk_source
        params = self._fk_params(source)
        if "service_type_field" in source:
            control.resolve_source = lambda c=control: self._resolve_fk_source(c)
            return lambda c=control, p=params: asyncio.to_thread(self._load_dynamic_fk, c, p)
        return lambda: asyncio.to_thread(load_fk_candidates, self.connection, source, params, self._fk_cache)

    def _resolve_fk_source(self, control: FkSelectControl) -> dict | None:
        """The effective service source for a dynamic ``serviceId`` control."""
        source = control.fk_source
        switch = source["service_type_field"]
        field = self.form.fields.get(switch)
        value = str(field.value) if field else ""
        return resolve_service_source(source, value)

    def _load_dynamic_fk(self, control: FkSelectControl, params: dict) -> list[dict]:
        """Load a dynamic FK control's candidates for the current serviceType."""
        if control.resolve_source is None:
            return []
        effective = control.resolve_source()
        if effective is None:
            return []
        return load_fk_candidates(self.connection, effective, params, self._fk_cache)

    def _fk_params(self, source: dict) -> dict:
        """Resolve an FK source's query params from the navigation context."""
        params: dict = {}
        for param, context_key in (source.get("params") or {}).items():
            value = self.context.get(context_key) or self.record.get(context_key)
            if value:
                params[param] = value
        return params

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
        self.app.push_screen(
            WizardScreen(
                self.connection,
                self.action,
                record=self.record,
                excluded=self.excluded,
                inject=self.inject,
                context=self.context,
                classes="Entities",
            )
        )

    def action_cancel(self) -> None:
        """Cancel the form."""
        self.dismiss(None)
