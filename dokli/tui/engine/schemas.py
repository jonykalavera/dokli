"""JSON Schema → pydantic model (for generic action forms)."""

import re
from typing import Any, Literal

from pydantic import BaseModel, Field, SecretStr, create_model

JSON_TO_ANNOTATION = {
    "string": str,
    "integer": int,
    "number": float,
    "boolean": bool,
    "array": list,
    "object": dict,
}

SECRET_KEY = re.compile(r"(?i)(password|secret|token|api[_-]?key|private[_-]?key|access[_-]?key)")

# Server-managed fields that should not be edited in forms.
READ_ONLY_FIELDS = {
    "createdAt",
    "updatedAt",
    "organizationId",
    "adminId",
    "applicationStatus",
    "composeStatus",
    "refreshToken",
}


def build_form_model(schema: dict, name: str = "ActionForm") -> type[BaseModel]:
    """Build a pydantic model from an OpenAPI request body schema.

    Used to reuse the existing generic :class:`~dokli.tui.forms.Form` widget,
    which derives controls and validation from a pydantic model. All fields are
    optional (default ``None``); requiredness is enforced by the form screen
    from the schema's ``required`` list.
    """
    fields: dict[str, Any] = {}
    for field_name, prop in schema.get("properties", {}).items():
        if field_name in READ_ONLY_FIELDS:
            continue
        annotation = _annotation_for(field_name, prop)
        label = _label_for(field_name)
        description = prop.get("description")
        if "enum" in prop:
            options = ", ".join(str(value) for value in prop["enum"])
            description = f"{description} [{options}]" if description else f"Options: {options}"
        fields[field_name] = (annotation | None, Field(None, title=label, description=description))
    return create_model(name, **fields)


def _annotation_for(field_name: str, prop: dict[str, Any]) -> Any:
    if SECRET_KEY.search(field_name):
        return SecretStr
    if "enum" in prop and prop.get("type") == "string":
        return Literal[tuple(prop["enum"])]
    return JSON_TO_ANNOTATION.get(str(prop.get("type")), str)


def _label_for(field_name: str) -> str:
    label = re.sub(r"(?<!^)(?=[A-Z])", " ", field_name).replace("_", " ")
    return label[:1].upper() + label[1:]
