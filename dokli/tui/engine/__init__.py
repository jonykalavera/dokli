"""Schema-driven TUI engine.

Parses the OpenAPI document into an entity registry so the TUI can render
generic list/detail/form views for any Dokploy API version.
"""

from dokli.tui.engine.icons import entity_icon, entity_icon_color, icon_label, state_color, state_indicator
from dokli.tui.engine.introspect import (
    collect_children,
    field_label,
    infer_columns,
    record_id,
    record_title,
)
from dokli.tui.engine.related import (
    PARAM_SOURCES,
    RELATED_ACTIONS,
    RELATED_PROVIDERS,
    list_verb_override,
    param_source,
    related_action_spec,
    related_records,
    related_spec,
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
    "PARAM_SOURCES",
    "RELATED_ACTIONS",
    "RELATED_PROVIDERS",
    "Entity",
    "EntityAction",
    "EntityRegistry",
    "action_bindings",
    "build_form_model",
    "classify",
    "collect_children",
    "entity_icon",
    "entity_icon_color",
    "field_label",
    "icon_label",
    "infer_columns",
    "key_for_verb",
    "list_verb_override",
    "nested_child_entity",
    "param_source",
    "parse_spec",
    "record_id",
    "record_title",
    "related_action_spec",
    "related_records",
    "related_spec",
    "state_color",
    "state_indicator",
]
