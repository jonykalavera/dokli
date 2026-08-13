"""Helpers to render live API data in generic views.

Dokploy's OpenAPI document does not describe response bodies, so list and
detail views infer their columns/fields from the actual data returned by the
API.
"""

import re
from typing import Any

NOISE_FIELDS = {"createdAt", "updatedAt", "refreshToken", "organizationId", "adminId", "env"}


def field_label(name: str) -> str:
    """Turn a camelCase/snake_case field name into a title."""
    label = re.sub(r"(?<!^)(?=[A-Z])", " ", name).replace("_", " ")
    return label[:1].upper() + label[1:]


def record_id(record: dict[str, Any], entity_name: str = "") -> str | None:
    """Best-effort id for a record."""
    if entity_name:
        candidate = record.get(f"{entity_name}Id")
        if candidate:
            return str(candidate)
    candidate = record.get("id")
    if candidate:
        return str(candidate)
    for key, value in record.items():
        if key.endswith("Id") and value:
            return str(value)
    return None


def record_title(record: dict[str, Any]) -> str:
    """A short title for a record (used in lists)."""
    # For mounts, prefer the host file path / volume name over the container
    # mount path (which is almost always "/").
    for key in ("name", "appName", "title", "label", "filePath", "volumeName", "mountPath"):
        value = record.get(key)
        if value:
            return str(value)
    return str(record_id(record) or "record")


def record_subtitle(record: dict[str, Any], entity_name: str = "") -> str:
    """A summary line for a record (used in lists)."""
    parts = []
    for key in ("description", "applicationStatus", "composeStatus"):
        value = record.get(key)
        if value:
            parts.append(f"{field_label(key)}: {value}")
    return " · ".join(parts)


def infer_columns(records: list[dict[str, Any]], entity_name: str = "") -> list[str]:
    """Pick columns for a list view from the first record."""
    if not records:
        return [entity_name or "record"]
    keys = list(records[0].keys())
    preferred = [f"{entity_name}Id", "id", "name", "appName", "description", "applicationStatus", "composeStatus"]
    columns = [key for key in preferred if key in keys]
    if not columns:
        columns = [key for key in keys if key not in NOISE_FIELDS][:4]
    return columns[:5]


def collect_children(record: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    """Flatten the nested child arrays of a record, tagged with their entity."""
    from dokli.tui.engine.spec import nested_child_entity

    children = []
    for key, value in record.items():
        child_entity = nested_child_entity(key)
        if not child_entity or not isinstance(value, list):
            continue
        for item in value:
            if isinstance(item, dict):
                children.append((child_entity, item))
    return children
