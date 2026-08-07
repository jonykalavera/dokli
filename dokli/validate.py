"""Offline manifest validation against the connection's schema (issue #50)."""

from dokli.api_client import APIClient
from dokli.config import ConnectionConfig
from dokli.manifest import Manifest
from dokli.resources import MATCH_KEYS, SERVICE_KINDS, parse_in
from dokli.tui.engine import parse_spec


def validate_manifest(connection: ConnectionConfig, manifest: Manifest) -> list[str]:
    """Validate a manifest against the connection's schema.

    Returns a list of issues (empty when valid).
    """
    issues = []
    registry = parse_spec(APIClient(connection).schema)
    for resource in manifest.resources:
        label = f"{resource.kind}:{resource.name}"
        entity = registry.get(resource.kind)
        if entity is None:
            issues.append(f"resource {label}: unknown kind '{resource.kind}'.")
            continue
        create = entity.get("create")
        update = entity.get("update")
        if create is None or update is None:
            issues.append(f"resource {label}: kind lacks create/update actions.")
            continue
        props = set(create.request_schema.get("properties", {})) | set(
            update.request_schema.get("properties", {})
        )
        for field in resource.data:
            if field not in props:
                issues.append(f"resource {label}: unknown field '{field}'.")
        key = MATCH_KEYS.get(resource.kind, "name")
        if key not in props:
            issues.append(f"resource {label}: match key '{key}' is not in the schema.")
        segments = parse_in(resource.in_)
        if not segments:
            issues.append(f"resource {label}: missing 'in:'.")
            continue
        parent_kind, _ = segments[-1]
        if parent_kind not in SERVICE_KINDS:
            issues.append(f"resource {label}: parent '{parent_kind}' is not supported yet.")
    return issues
