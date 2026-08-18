"""Offline manifest validation against the connection's schema (issue #50)."""

from dokli.api_client import APIClient
from dokli.config import ConnectionConfig
from dokli.manifest import Manifest, Resource
from dokli.resources import (
    MATCH_KEYS,
    NAMED_REFERENCES,
    PARENT_KINDS,
    SERVICE_KINDS,
    entity_name,
    parse_in,
)
from dokli.tui.engine import parse_spec
from dokli.tui.engine.spec import EntityRegistry


def validate_manifest(connection: ConnectionConfig, manifest: Manifest) -> list[str]:
    """Validate a manifest against the connection's schema.

    Returns a list of issues (empty when valid).
    """
    registry = parse_spec(APIClient(connection).schema)
    issues: list[str] = []
    for resource in manifest.resources:
        issues.extend(_validate_resource(resource, registry))
    return issues


def _validate_resource(resource: Resource, registry: EntityRegistry) -> list[str]:
    """Validate a single generic resource against the entity registry."""
    issues: list[str] = []
    label = f"{resource.kind}:{resource.name}"
    entity = registry.get(entity_name(resource.kind))
    if entity is None:
        return [f"resource {label}: unknown kind '{resource.kind}'."]
    create = entity.get("create")
    update = entity.get("update")
    if create is None or update is None:
        return [f"resource {label}: kind lacks create/update actions."]
    create_schema = create.request_schema
    props = set(create_schema.get("properties", {})) | set(update.request_schema.get("properties", {}))
    key = MATCH_KEYS.get(resource.kind, "name")
    if key not in props:
        issues.append(f"resource {label}: match key '{key}' is not in the schema.")
    for field in resource.data:
        if field == NAMED_REFERENCES.get(resource.kind):
            continue
        if field not in props:
            issues.append(f"resource {label}: unknown field '{field}'.")
    for field in create_schema.get("required", []):
        if field in resource.data or field == key or field.endswith("Id"):
            continue
        prop = create_schema.get("properties", {}).get(field, {})
        if "default" not in prop:
            issues.append(f"resource {label}: missing required field '{field}'.")
    segments = parse_in(resource.in_)
    if not segments:
        issues.append(f"resource {label}: missing 'in:'.")
        return issues
    parent_kind, _ = segments[-1]
    if parent_kind not in SERVICE_KINDS:
        issues.append(f"resource {label}: parent '{parent_kind}' is not supported yet.")
        return issues
    allowed = PARENT_KINDS.get(resource.kind)
    if allowed is not None and parent_kind not in allowed:
        issues.append(
            f"resource {label}: cannot hang off '{parent_kind}' " f"(allowed: {', '.join(sorted(allowed))})."
        )
    return issues
