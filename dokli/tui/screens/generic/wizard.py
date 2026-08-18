"""Step-by-step wizard form (one field at a time)."""

import asyncio
from typing import TYPE_CHECKING

from textual.binding import Binding
from textual.containers import Container, Horizontal
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Label, Select

from dokli.config import ConnectionConfig
from dokli.tui.engine import EntityAction, build_form_model
from dokli.tui.engine.conditionals import conditional_switches
from dokli.tui.engine.fk import load_fk_candidates
from dokli.tui.forms import FkSelectControl, FormControl, compute_conditional_hidden
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
        context: dict | None = None,
        *args,
        **kwargs,
    ) -> None:
        """Construct the wizard screen."""
        super().__init__(*args, **kwargs)
        self.connection = connection
        self.action = action
        self.record = record or {}
        self.inject = inject or {}
        self.context = context or {}
        self._fk_cache: dict = {}
        self.model = build_form_model(action.request_schema, name=f"{action.route}Wizard", excluded=excluded or set())
        self.fields = list(self.model.model_fields.items())
        self.controls = {
            name: FormControl.from_field(name, field, value=self.record.get(name)) for name, field in self.fields
        }
        for control in self.controls.values():
            if isinstance(control, FkSelectControl):
                control.fetch = lambda c=control: asyncio.to_thread(
                    load_fk_candidates, self.connection, c.fk_source, self._fk_params(c.fk_source), self._fk_cache
                )
        self.conditional = conditional_switches(action.route.split(".")[0])
        self._hidden: set[str] = set()
        self._order: list[str] = []
        self._current = ""
        self.index = 0
        self._recompute_visible()

    def _fk_params(self, source: dict) -> dict:
        """Resolve an FK source's query params from the navigation context."""
        params: dict = {}
        for param, context_key in (source.get("params") or {}).items():
            value = self.context.get(context_key) or self.record.get(context_key)
            if value:
                params[param] = value
        return params

    def _recompute_visible(self) -> None:
        """Rebuild the ordered list of currently visible fields."""
        values = {
            spec["switch"]: str(self.controls[spec["switch"]].value)
            for spec in self.conditional
            if spec.get("switch") in self.controls
        }
        self._hidden = compute_conditional_hidden(self.conditional, values)
        self._order = [name for name, _ in self.fields if name not in self._hidden]

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

    def on_select_changed(self, event: Select.Changed) -> None:
        """Re-evaluate visibility when a conditional switch changes."""
        if any(f"{spec.get('switch')}-input" == event.select.id for spec in self.conditional):
            self._recompute_visible()
            if self._current in self._order:
                self.query_one("#prompt", Label).update(
                    f"({self.index + 1}/{len(self._order)}) {self.controls[self._current].label}"
                )
            else:
                self.index = min(self.index, len(self._order) - 1)
                self._show()

    def _show(self) -> None:
        if not self._order:
            self._finish()
            return
        self.index = min(max(self.index, 0), len(self._order) - 1)
        name = self._order[self.index]
        control = self.controls[name]
        container = self.query_one("#control", Container)
        container.remove_children()
        container.mount(control)
        self.query_one("#prompt", Label).update(f"({self.index + 1}/{len(self._order)}) {control.label}")
        control.focus()
        self._current = name

    def action_next(self) -> None:
        """Advance to the next visible field, or finish on the last one."""
        if self.index < len(self._order) - 1:
            self.index += 1
            self._show()
        else:
            self._finish()

    def action_back(self) -> None:
        """Go back to the previous visible field."""
        if self.index > 0:
            self.index -= 1
            self._show()

    def action_cancel(self) -> None:
        """Cancel the wizard."""
        self.dismiss(None)

    def _finish(self) -> None:
        data = {name: self.controls[name].get_data() for name in self._order}
        required = [name for name in self.action.request_schema.get("required", []) if name in self._order]
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
