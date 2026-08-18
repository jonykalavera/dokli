"""Forms for TUI."""

import json
from dataclasses import dataclass
from types import NoneType, UnionType
from typing import TYPE_CHECKING, Any, Generic, Literal, TypeVar, Union, get_args, get_origin

import httpx
from pydantic import BaseModel, SecretBytes, SecretStr, ValidationError
from pydantic_core import ErrorDetails
from textual.containers import Container
from textual.css.query import NoMatches
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import Input, Label, Select, Static, Switch, TextArea

from dokli.tui.engine.fk import candidate_options

if TYPE_CHECKING:
    from textual.app import ComposeResult
    from textual.timer import Timer


M = TypeVar("M", bound=BaseModel)


def _core_annotation(annotation: Any) -> Any:
    """Strip ``None`` from an ``X | None`` union annotation."""
    origin = get_origin(annotation)
    if origin is Union or origin is UnionType:
        non_none = [arg for arg in get_args(annotation) if arg is not NoneType]
        if len(non_none) == 1:
            return non_none[0]
    return annotation


def _is_optional(annotation: Any) -> bool:
    """Whether an annotation allows ``None``."""
    origin = get_origin(annotation)
    return (origin is Union or origin is UnionType) and NoneType in get_args(annotation)


def _apply_field_defaults(model: type[BaseModel], data: dict[str, Any]) -> dict[str, Any]:
    """Replace ``None`` with the field default for non-optional fields.

    Empty inputs yield ``None`` from ``get_data``; a non-optional field (e.g.
    ``notes: str = ""``) must fall back to its default instead of failing
    validation.
    """
    resolved = dict(data)
    for name, field in model.model_fields.items():
        if name in resolved and resolved[name] is None and not _is_optional(field.annotation):
            default = field.get_default(call_default_factory=True)
            if default is not None:
                resolved[name] = default
    return resolved


class FormControl(Static):
    """Base form control widget."""

    label = reactive("")
    value: reactive[Any] = reactive("")
    placeholder = reactive("")
    default: reactive[Any] = reactive("")
    error: reactive[ErrorDetails | None] = reactive(None)

    def __init__(
        self,
        id: str,
        label: str,
        value: Any = "",
        placeholder: str = "",
        default: Any = "",
        error: ErrorDetails | None = None,
        **kwargs,
    ) -> None:
        """Construct a form control widget."""
        super().__init__(id=id, **kwargs)
        self.label = label
        self.value = value if value is not None else ""
        self.placeholder = placeholder
        self.default = default if default is not None else ""
        self.error = error

    def compose(self) -> "ComposeResult":
        """Yield the label and error label (inputs are added by subclasses)."""
        yield Label(
            self.label,
            id=f"{self.id}-label",
            classes="hidden form-label" if not self.label else "form-label",
        )
        yield Label(
            str(self.error) if self.error else "ERRORR",
            id=f"{self.id}-error",
            classes="error-msg",
        )

    def get_data(self) -> Any:
        """The value to submit for this control (``None`` when empty)."""
        return None if self.value in ("", None) else self.value

    @staticmethod
    def from_field(name, field, **kwargs) -> "FormControl":
        """Construct a form control from a pydantic field."""
        annotation = _core_annotation(field.annotation)
        base = dict(
            label=field.title if field.title else name.replace("_", " ").title(),
            placeholder=field.description or "",
        )
        base.update(kwargs)
        extra = getattr(field, "json_schema_extra", None) or {}
        value = kwargs.get("value", "")
        if annotation is bool:
            return SwitchControl(id=name, **base)  # ty: ignore[invalid-argument-type]
        if get_origin(annotation) is Literal:
            return SelectControl(id=name, options=list(get_args(annotation)), **base)
        if extra.get("fk"):
            return FkSelectControl(id=name, fk_source=extra["fk"], **base)
        if annotation in (list, dict):
            return TextAreaControl(id=name, parse_json=True, **base)
        if annotation is str and (extra.get("multiline") or (isinstance(value, str) and "\n" in value)):
            return TextAreaControl(id=name, parse_json=False, **base)
        return TextControl(id=name, password=annotation in (SecretStr, SecretBytes), **base)

    def watch_error(self, old_value: ErrorDetails | None, new_value: ErrorDetails | None) -> None:
        """Watch error changes."""
        self.classes = (self.classes - {"error"}) if new_value is None else {"error", *self.classes}
        try:
            error = self.query_one(f"#{self.id}-error")
            assert isinstance(error, Label), "should be a label"
            error.renderable = new_value.get("msg") or "" if new_value else ""
        except NoMatches:
            pass

    def reset(self, reset_classes=True, reset_value=True, reset_error=True) -> None:
        """Reset."""
        if reset_value:
            self.value = self.default
        if reset_classes:
            self.classes = []
        if reset_error:
            self.error = None


class TextControl(FormControl):
    """A single-line text/number/password input."""

    def __init__(self, id: str, value: Any = "", password: bool = False, **kwargs) -> None:
        """Construct a text control."""
        super().__init__(id=id, value=value, **kwargs)
        self.password = password

    def compose(self) -> "ComposeResult":
        """Yield the widgets."""
        yield from super().compose()
        yield Input(
            "" if self.value in ("", None) else str(self.value),
            id=f"{self.id}-input",
            placeholder=self.placeholder,
            password=self.password,
        )

    def watch_value(self, old_value: Any, new_value: Any) -> None:
        """Watch value changes.

        Only writes back to the input when the value actually differs, so user
        typing (which also sets ``value``) does not reset the cursor.
        """
        try:
            input = self.query_one(f"#{self.id}-input")
            assert isinstance(input, Input)
            text = "" if new_value in ("", None) else str(new_value)
            if input.value != text:
                input.value = text
        except NoMatches:
            pass

    def on_input_changed(self, event: Input.Changed) -> None:
        """On input changed."""
        self.value = event.value


class SelectControl(FormControl):
    """A dropdown for string enums."""

    def __init__(self, id: str, options: list[str], value: Any = "", **kwargs) -> None:
        """Construct a select control."""
        super().__init__(id=id, value=value, **kwargs)
        self.options = options

    def compose(self) -> "ComposeResult":
        """Yield the widgets."""
        yield from super().compose()
        current = self.value if self.value in self.options else Select.BLANK
        yield Select(
            [(str(option), option) for option in self.options],
            value=current,
            prompt="Select...",
            id=f"{self.id}-input",
        )

    def watch_value(self, old_value: Any, new_value: Any) -> None:
        """Watch value changes."""
        try:
            select = self.query_one(f"#{self.id}-input")
            assert isinstance(select, Select)
            select.value = new_value if new_value in self.options else Select.BLANK
        except NoMatches:
            pass

    def on_select_changed(self, event: Select.Changed) -> None:
        """On select changed."""
        self.value = "" if event.value is Select.BLANK else event.value


class FkSelectControl(FormControl):
    """A dropdown of candidates for a foreign-key id field.

    Candidates come from the curated ``fk_source`` route (e.g. ``serverId`` →
    ``server.all``). The dropdown is populated lazily on mount; when the source
    is unreachable or empty the control falls back to a free-text input.
    """

    def __init__(self, id: str, fk_source: dict, value: Any = "", **kwargs) -> None:
        """Construct an FK select control."""
        super().__init__(id=id, value=value, **kwargs)
        self.fk_source = fk_source
        self.fetch = None
        self._options: list[tuple[str, str]] = []

    def compose(self) -> "ComposeResult":
        """Yield the label, error, and a container for the live control."""
        yield from super().compose()
        yield Container(id=f"{self.id}-wrap")

    async def on_mount(self) -> None:
        """Fetch candidates and render a Select or a free-text fallback."""
        if self.fetch is None:
            self._mount_text()
            return
        try:
            records = await self.fetch()
        except httpx.HTTPError:
            self._mount_text()
            return
        self._options = candidate_options(records, self.fk_source)
        if not self._options or (self.value and self.value not in [v for _, v in self._options]):
            self._mount_text()
            return
        self._mount_select()

    def _mount_select(self) -> None:
        """Render the dropdown with the current value preselected when present."""
        wrap = self.query_one(f"#{self.id}-wrap", Container)
        current = self.value if self.value in [v for _, v in self._options] else Select.BLANK
        wrap.mount(Select(self._options, value=current, prompt="Select...", id=f"{self.id}-input"))

    def _mount_text(self) -> None:
        """Render a free-text input (fallback when there are no candidates)."""
        wrap = self.query_one(f"#{self.id}-wrap", Container)
        wrap.mount(
            Input(
                "" if self.value in ("", None) else str(self.value),
                id=f"{self.id}-input",
                placeholder=self.placeholder,
            )
        )

    def watch_value(self, old_value: Any, new_value: Any) -> None:
        """Sync the mounted widget with programmatic value changes."""
        try:
            widget = self.query_one(f"#{self.id}-input")
        except NoMatches:
            return
        if isinstance(widget, Select):
            widget.value = new_value if new_value in [v for _, v in self._options] else Select.BLANK
        elif isinstance(widget, Input):
            text = "" if new_value in ("", None) else str(new_value)
            if widget.value != text:
                widget.value = text

    def on_select_changed(self, event: Select.Changed) -> None:
        """On select changed."""
        self.value = "" if event.value is Select.BLANK else event.value

    def on_input_changed(self, event: Input.Changed) -> None:
        """On input changed."""
        self.value = event.value


class SwitchControl(FormControl):
    """A boolean toggle."""

    def compose(self) -> "ComposeResult":
        """Yield the widgets."""
        yield from super().compose()
        yield Switch(value=bool(self.value), id=f"{self.id}-input")

    def watch_value(self, old_value: Any, new_value: Any) -> None:
        """Watch value changes."""
        try:
            switch = self.query_one(f"#{self.id}-input")
            assert isinstance(switch, Switch)
            switch.value = bool(new_value)
        except NoMatches:
            pass

    def on_switch_changed(self, event: Switch.Changed) -> None:
        """On switch changed."""
        self.value = event.value

    def get_data(self) -> Any:
        """The boolean value."""
        return bool(self.value)


class TextAreaControl(FormControl):
    """A text area for multi-line strings or JSON objects/arrays."""

    def __init__(self, id: str, value: Any = "", parse_json: bool = True, **kwargs) -> None:
        """Construct a text area control."""
        if isinstance(value, dict | list):
            value = json.dumps(value)
        super().__init__(id=id, value=value, **kwargs)
        self.parse_json = parse_json

    def compose(self) -> "ComposeResult":
        """Yield the widgets."""
        yield from super().compose()
        yield TextArea("" if self.value in ("", None) else str(self.value), id=f"{self.id}-input")

    def watch_value(self, old_value: Any, new_value: Any) -> None:
        """Watch value changes.

        Only writes back to the text area when the text actually differs, so
        user typing (which also sets ``value``) does not reset the cursor.
        """
        try:
            area = self.query_one(f"#{self.id}-input")
            assert isinstance(area, TextArea)
            text = "" if new_value in ("", None) else str(new_value)
            if area.text != text:
                area.text = text
        except NoMatches:
            pass

    def on_text_area_changed(self, event: TextArea.Changed) -> None:
        """On text area changed."""
        self.value = event.text_area.text

    def get_data(self) -> Any:
        """Parse JSON when the field is an object/array, otherwise return the text."""
        if not self.parse_json:
            return None if self.value in ("", None) else self.value
        if self.value in ("", None):
            return None
        try:
            return json.loads(self.value)
        except (json.JSONDecodeError, TypeError):
            return self.value


class Form(Generic[M], Container):
    """Form Widget."""

    @dataclass
    class FormValid(Message):
        """Form is valid."""

        data: dict[str, Any]
        instance: BaseModel | None

    class FormInvalid(Message):
        """Form is invalid."""

    data: reactive[dict[str, Any]] = reactive(dict)  # ty: ignore[invalid-assignment]
    model: reactive[type[M] | None] = reactive(None)
    error: reactive[str | None] = reactive(None)
    cleaned_data: dict[str, Any] | None = None
    instance: M | None = None

    def __init__(
        self,
        *controls: FormControl,
        data: dict[str, Any] | None = None,
        instance: M | None = None,
        model: type[M] | None = None,
        validate_on_input: bool = True,
        **kwargs,
    ) -> None:
        """Construct a form widget."""
        super().__init__(*controls, **kwargs)
        self.fields = {c.id: c for c in controls if isinstance(c, FormControl)}
        self.instance = instance
        self.data = data or (instance.model_dump() if instance else {})
        self.model = model if not instance else type(instance)
        self.cleaned_data = None
        self.validate_on_input = validate_on_input
        self._validate_timer: Timer | None = None

    async def on_mount(self) -> None:
        """On mount, add the form-level error label."""
        self._error_label = Label("", classes="form-error")
        await self.mount(self._error_label)

    def watch_error(self, old_value: str | None, new_value: str | None) -> None:
        """Show or hide the form-level error message."""
        label = getattr(self, "_error_label", None)
        if label is None:
            return
        label.update(new_value or "")
        label.set_class(bool(new_value), "visible")

    @classmethod
    def from_model(
        cls,
        model: type[M],
        instance: M | None = None,
        data: dict[str, Any] | None = None,
        **kwargs,
    ) -> "Form":
        """Construct a form from a model.

        Controls are prefilled from ``data`` when given, otherwise from the
        ``instance``.
        """
        if data is None:
            data = cls._get_data_from_instance(instance)
        controls = (
            FormControl.from_field(name=name, field=field, value=data.get(name))
            for n, (name, field) in enumerate(model.model_fields.items())
        )
        return cls(*controls, model=model, instance=instance, data=data, **kwargs)

    @classmethod
    def _get_data_from_instance(cls, instance: BaseModel | None) -> dict[str, Any]:
        return {} if instance is None else json.loads(instance.model_dump_json())

    def _validate_on_input(self) -> None:
        """Debounce live validation so rapid typing/backspace does not stall."""
        if not self.validate_on_input:
            return
        if self._validate_timer is not None:
            self._validate_timer.stop()
        self._validate_timer = self.set_timer(0.15, self._validate_now)

    def _validate_now(self) -> None:
        """Run a deferred validation (from the debounce timer)."""
        self._validate_timer = None
        self.validate()

    def on_input_changed(self, event: Input.Changed) -> None:
        """On input changed."""
        self._validate_on_input()

    def on_select_changed(self, event: Select.Changed) -> None:
        """On select changed."""
        self._validate_on_input()

    def on_switch_changed(self, event: Switch.Changed) -> None:
        """On switch changed."""
        self._validate_on_input()

    def on_text_area_changed(self, event: TextArea.Changed) -> None:
        """On text area changed."""
        self._validate_on_input()

    def validate(self) -> bool:
        """Validate form data against model, if any."""
        data = self._get_form_data()
        self.reset(reset_value=False)
        self.error = None
        if not self.model:
            self.cleaned_data = data
            return True
        try:
            self.instance = self.model.model_validate(_apply_field_defaults(self.model, data))
            self.cleaned_data = self.instance.model_dump()
            self.post_message(self.FormValid(data=self.cleaned_data or {}, instance=self.instance))
            return True
        except ValidationError as err:
            self._set_errors(err.errors())
            self.post_message(self.FormInvalid())
        return False

    @property
    def is_valid(self):
        """Return whether the form is valid."""
        return self.validate()

    def reset(
        self,
        reset_value=True,
        reset_classes=True,
        reset_instance=True,
        reset_cleaned_data=True,
    ) -> None:
        """Reset."""
        if reset_cleaned_data:
            self.cleaned_data = None
        if reset_instance:
            self.instance = None
        for child in self.children:
            if not isinstance(child, FormControl):
                continue
            child.reset(reset_value=reset_value, reset_classes=reset_classes)

    def _set_errors(self, errors: list[ErrorDetails]) -> None:
        for error in errors:
            loc = error["loc"]
            if not loc:
                # Model-level validation error (e.g. a cross-field validator
                # like "provide api_key or api_key_cmd"); no field to attach to.
                self.error = error["msg"].removeprefix("Value error, ")
                continue
            field = self.fields.get(str(loc[-1]))
            assert field, f"Unknown field: {loc}"
            field.error = error

    def _get_form_data(self) -> dict[str, Any]:
        data = {child.id: child.get_data() for child in self.children if child.id and isinstance(child, FormControl)}
        return data
