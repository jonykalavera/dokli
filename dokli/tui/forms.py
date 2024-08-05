"""Forms for TUI."""

import json
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Generic, TypeVar

from pydantic import BaseModel, SecretBytes, SecretStr, ValidationError
from pydantic_core import ErrorDetails
from textual import log
from textual.containers import Container
from textual.css.query import NoMatches
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import Input, Label, Static

if TYPE_CHECKING:
    from textual.app import ComposeResult


M = TypeVar("M", bound=BaseModel)


class FormControl(Static):
    """Form control widget."""

    label = reactive("")
    value = reactive("")
    placeholder = reactive("")
    default = reactive("")
    error: reactive[ErrorDetails | None] = reactive(None)

    def __init__(
        self,
        id: str,
        label: str,
        value: str = "",
        placeholder: str = "",
        default: str = "",
        error: ErrorDetails | None = None,
        password: bool = False,
        **kwargs,
    ) -> None:
        """Construct a form control widget."""
        super().__init__(id=id, **kwargs)
        self.label = label
        self.value = value
        self.placeholder = placeholder
        self.default = default
        self.password = password
        self.error = error

    def compose(self) -> "ComposeResult":
        """Yield children widgets."""
        yield Label(
            self.label,
            id=f"{self.id}-label",
            classes="hidden form-label" if not self.label else "form-label",
        )
        yield Input(
            self.value,
            id=f"{self.id}-input",
            placeholder=self.placeholder,
            password=self.password,
        )
        yield Label(
            str(self.error) if self.error else "ERRORR",
            id=f"{self.id}-error",
            classes="error-msg",
        )

    @staticmethod
    def from_field(name, field, **kwargs) -> "FormControl":
        """Construct a form control from a pydantic field."""
        return FormControl(
            id=name,
            label=field.title if field.title else name.replace("_", " ").title(),
            placeholder=field.description or "",
            password=field.annotation in (SecretStr, SecretBytes),
            **kwargs,
        )

    def watch_value(self, old_value: str, new_value: str) -> None:
        """Watch value changes."""
        self.value = new_value
        try:
            input = self.query_one(f"#{self.id}-input")
            assert isinstance(input, Input)
            input.value = new_value
        except NoMatches:
            pass

    def watch_error(self, old_value: ErrorDetails | None, new_value: ErrorDetails | None) -> None:
        """Watch error changes."""
        self.classes = (self.classes - {"error"}) if new_value is None else {"error", *self.classes}
        try:
            error = self.query_one(f"#{self.id}-error")
            assert isinstance(error, Label), "should be a label"
            error.renderable = new_value.get("msg") or "" if new_value else ""
        except NoMatches:
            pass

    def on_input_changed(self, event: Input.Changed) -> None:
        """On input changed."""
        self.value = event.value

    def reset(self, reset_classes=True, reset_value=True, reset_error=True) -> None:
        """Reset."""
        if reset_value:
            self.value = self.default
        if reset_classes:
            self.classes = []
        if reset_error:
            self.error = None


class Form(Generic[M], Container):
    """Form Widget."""

    @dataclass
    class FormValid(Message):
        """Form is valid."""

        data: dict[str, Any]
        instance: BaseModel | None

    class FormInvalid(Message):
        """Form is invalid."""

    data: reactive[dict[str, Any]] = reactive(dict)
    model: reactive[type[M] | None] = reactive(None)
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

    @classmethod
    def from_model(cls, model: type[M], instance: M | None = None, **kwargs) -> "Form":
        """Construct a form form a model."""
        data = cls._get_data_from_instance(instance)
        log("Form", data)
        controls = (
            FormControl.from_field(name=name, field=field, value=data.get(name, ""))
            for n, (name, field) in enumerate(model.model_fields.items())
        )
        return cls(*controls, model=model, instance=instance, **kwargs)

    @classmethod
    def _get_data_from_instance(cls, instance: BaseModel | None) -> dict[str, Any]:
        return {} if instance is None else json.loads(instance.model_dump_json())

    def on_input_changed(self, event: Input.Changed) -> None:
        """On input changed."""
        if self.validate_on_input:
            self.validate()

    def validate(self) -> bool:
        """Validate form data against model, if any."""
        data = self._get_form_data()
        self.reset(reset_value=False)
        if not self.model:
            self.cleaned_data = data
            return True
        try:
            self.instance = self.model.model_validate(data)
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
            loc = str(error["loc"][-1])
            field = self.fields.get(loc)
            assert field, f"Unknown field: {loc}"
            field.error = error

    def _get_form_data(self) -> dict[str, Any]:
        data = {child.id: child.value for child in self.children if child.id and isinstance(child, FormControl)}
        return data
