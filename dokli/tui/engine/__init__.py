"""Schema-driven TUI engine.

Parses the OpenAPI document into an entity registry so the TUI can render
generic list/detail/form views for any Dokploy API version.
"""

from dokli.tui.engine.introspect import (
    collect_children,
    field_label,
    infer_columns,
    record_id,
    record_subtitle,
    record_title,
)
from dokli.tui.engine.schemas import build_form_model
from dokli.tui.engine.spec import (
    DESTRUCTIVE_VERBS,
    Entity,
    EntityAction,
    EntityRegistry,
    action_bindings,
    classify,
    key_for_verb,
    nested_child_entity,
    parse_spec,
)

__all__ = [
    "DESTRUCTIVE_VERBS",
    "Entity",
    "EntityAction",
    "EntityRegistry",
    "action_bindings",
    "build_form_model",
    "classify",
    "collect_children",
    "field_label",
    "infer_columns",
    "key_for_verb",
    "nested_child_entity",
    "parse_spec",
    "record_id",
    "record_subtitle",
    "record_title",
]
