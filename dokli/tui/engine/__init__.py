"""Schema-driven TUI engine.

Parses the OpenAPI document into an entity registry so the TUI can render
generic list/detail/form views for any Dokploy API version.
"""

from dokli.tui.engine.introspect import field_label, infer_columns, record_id, record_subtitle, record_title
from dokli.tui.engine.schemas import build_form_model
from dokli.tui.engine.spec import Entity, EntityAction, EntityRegistry, classify, parse_spec

__all__ = [
    "Entity",
    "EntityAction",
    "EntityRegistry",
    "build_form_model",
    "classify",
    "field_label",
    "infer_columns",
    "parse_spec",
    "record_id",
    "record_subtitle",
    "record_title",
]
