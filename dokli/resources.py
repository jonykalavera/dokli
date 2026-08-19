"""Generic schema-driven resources (issue #50).

A generic manifest resource (``kind`` + ``name`` + ``in`` + ``data``) is
resolved against the entity registry and the live instance. The schema
conventions are followed by default; the curated maps below cover the known
historical exceptions (kinds without a stable ``name``, parents addressed via
``serviceId`` instead of ``<parent>Id``, entities whose API name differs from
the manifest ``kind``).
"""

import re
import subprocess
from typing import TYPE_CHECKING, Any

from dokli.manifest import Resource
from dokli.report import ApplyAction
from dokli.tui.engine import parse_spec
from dokli.tui.engine.spec import NESTED_CHILD_KEYS, EntityRegistry

if TYPE_CHECKING:
    from dokli.state import State

# Kinds whose match key is not their ``name`` field (historical exceptions).
MATCH_KEYS: dict[str, str] = {
    "domain": "host",
    "port": "publishedPort",
    "redirects": "regex",
    "security": "username",
    "mount": "filePath",
    "backup": "schedule",
}

# Manifest kind -> API entity name when they differ.
ENTITY_NAMES: dict[str, str] = {
    "mount": "mounts",
}

# Child kind -> the id field on its record (defaults to f"{kind}Id").
ID_FIELDS: dict[str, str] = {
    "mount": "mountId",
    "redirects": "redirectId",
    "domain": "domainId",
    "port": "portId",
    "security": "securityId",
    "backup": "backupId",
    "schedule": "scheduleId",
}

# Kinds that address their parent with a specific id field (default <parent>Id).
PARENT_ID_FIELDS: dict[str, str] = {
    "mount": "serviceId",
    "port": "applicationId",
    "security": "applicationId",
    "redirects": "applicationId",
}

# Kinds that only hang off specific service parents (None = any service).
PARENT_KINDS: dict[str, set[str] | None] = {
    "domain": {"application", "compose", "previewDeployment"},
    "port": {"application"},
    "security": {"application"},
    "redirects": {"application"},
    "schedule": {"application", "compose"},
    "backup": {"postgres", "mysql", "mariadb", "mongo", "redis", "libsql", "compose"},
    "mount": None,
}

# Kinds whose update requires fields the create may not set; the live child
# record is merged into the update payload so those fields are preserved.
UPDATE_MERGE_KINDS = frozenset({"backup", "schedule"})

# Data fields that are resolved by name (never sent as-is), and how.
NAMED_REFERENCES: dict[str, str] = {"backup": "destination"}

# Kinds whose children are fetched via a list route (route, id param, type
# param) instead of a nested array on the parent record.
LIST_LOOKUP: dict[str, tuple[str, str, str]] = {
    "schedule": ("schedule.list", "id", "scheduleType"),
}

# Child kinds exported as generic resources, and the fields emitted per kind
# (ids, parent ids and read-only fields are never exported; secrets omitted).
EXPORT_FIELDS: dict[str, set[str]] = {
    "domain": {"host", "https", "path", "port", "domainType"},
    "port": {"publishedPort", "targetPort", "protocol", "publishMode"},
    "security": {"username"},
    "redirects": {"regex", "replacement", "permanent"},
    "mount": {"type", "mountPath", "filePath", "content"},
    "schedule": {"name", "cronExpression", "command", "enabled", "serviceName", "shellType", "scheduleType"},
    "backup": {"schedule", "prefix", "database", "databaseType", "enabled", "keepLatestCount", "backupType"},
}

# Fields that are never exported (secrets), per kind.
SECRET_FIELDS: dict[str, set[str]] = {
    "security": {"password"},
    "backup": {"metadata"},
}

# Fields only exported with --include-secrets (redacted by default).
SECRET_OPT_FIELDS: dict[str, set[str]] = {
    "mount": {"content"},
}

# Extra required fields for delete routes that have no schema default.
DELETE_DEFAULTS: dict[str, dict[str, Any]] = {"compose": {"deleteVolumes": False}}


def build_registry(client) -> EntityRegistry:
    """Parse the client's schema into an entity registry (empty if unavailable)."""
    schema = getattr(client, "schema", None)
    return parse_spec(schema) if isinstance(schema, dict) else EntityRegistry()


def fetch_children(client, kind: str, parent_kind: str, service_id: str, parent_record: dict) -> list[dict]:
    """Fetch the live children of a resource kind for a parent service."""
    lookup = LIST_LOOKUP.get(kind)
    if lookup is not None:
        route, id_param, type_param = lookup
        raw = client.request("GET", route, {id_param: service_id, type_param: parent_kind}).json()
        return raw if isinstance(raw, list) else raw.get("items", [])
    return parent_record.get(child_array_key(kind)) or []


def delete_spec(registry, kind: str) -> tuple[str, str, dict] | None:
    """The delete route, id field and required defaults for a kind.

    Derived from the entity's destructive actions (``delete``/``remove``) plus
    curated defaults for required fields without a schema default.
    """
    entity = entity_name(kind)
    spec = registry.get(entity)
    if spec is None:
        return None
    for verb in ("delete", "remove"):
        action = spec.get(verb)
        if action is None:
            continue
        schema = action.request_schema
        required = schema.get("required", [])
        id_field = next((field for field in required if field.endswith("Id")), f"{entity}Id")
        defaults = dict(DELETE_DEFAULTS.get(kind, {}))
        for field in required:
            if field.endswith("Id") or field in defaults:
                continue
            prop = schema.get("properties", {}).get(field, {})
            if "default" in prop:
                defaults[field] = prop["default"]
        return f"{entity}.{verb}", id_field, defaults
    return None


# Child kind -> the nested array key on the parent service record.
CHILD_ARRAY: dict[str, str] = {child: key for key, child in NESTED_CHILD_KEYS.items()}

# Service kinds that can host leaf resources.
SERVICE_KINDS = frozenset({"compose", "application", "postgres", "mysql", "mariadb", "mongo", "redis", "libsql"})


def match_key(kind: str) -> str:
    """The field used to match a resource kind against the live instance."""
    return MATCH_KEYS.get(kind, "name")


def child_array_key(kind: str) -> str:
    """The nested array key of a child kind on the parent service record."""
    try:
        return CHILD_ARRAY[kind]
    except KeyError:
        raise ValueError(f"Kind '{kind}' is not a known child resource.") from None


def entity_name(kind: str) -> str:
    """The API entity name for a manifest kind."""
    return ENTITY_NAMES.get(kind, kind)


def id_field(kind: str) -> str:
    """The id field of a resource kind's record."""
    return ID_FIELDS.get(kind, f"{kind}Id")


def parse_in(path: str | None) -> list[tuple[str, str]]:
    """Parse an ``in`` path into ``(kind, name)`` segments.

    Segments are ``<kind>:<name>``, e.g. ``compose:torrents`` or
    ``project:media / environment:production / compose:torrents``.
    """
    segments: list[tuple[str, str]] = []
    for raw in (path or "").split("/"):
        part = raw.strip()
        if not part:
            continue
        if ":" in part:
            kind, name = part.split(":", 1)
            segments.append((kind.strip(), name.strip()))
        else:
            segments.append(("", part))
    return segments


def match_value(resource: Resource, key: str) -> str:
    """The value to match on, falling back to the resource name."""
    return str(resource.data.get(key) or resource.name)


def resolve_data(data: dict[str, Any]) -> dict[str, Any]:
    """Resolve secret references (``{"cmd": ...}`` / ``{"keyring": ...}``) in data."""
    return {key: _resolve_secret(value) for key, value in data.items()}


_ENV_REF = re.compile(r"^\{(cmd|keyring):\s*(.+)\}$", re.DOTALL)


def resolve_env(env: str) -> str:
    """Resolve ``{cmd: ...}`` / ``{keyring: ...}`` references in ``KEY=VALUE`` env lines.

    A value that is exactly a single reference is resolved (same semantics as
    ``resolve_data``); plain lines pass through untouched.
    """
    lines: list[str] = []
    for line in env.splitlines():
        if "=" not in line:
            lines.append(line)
            continue
        key, _, value = line.partition("=")
        match = _ENV_REF.match(value.strip())
        if match is None:
            lines.append(line)
            continue
        kind, payload = match.group(1), match.group(2).strip()
        payload = payload.strip().strip('"').strip("'")
        lines.append(f"{key}={_resolve_secret({kind: payload})}")
    return "\n".join(lines)


def env_changed(resolved_env: str, live_env: str | None) -> bool:
    """Whether resolved manifest env differs from the live env, ignoring line order.

    Docker compose env order is insignificant; comparing sorted ``KEY=VALUE``
    lines avoids spurious plan/apply churn.
    """
    desired = sorted(line for line in resolved_env.splitlines() if line)
    current = sorted(line for line in (live_env or "").splitlines() if line)
    return desired != current


def _resolve_secret(value: Any) -> Any:
    if isinstance(value, dict) and set(value) <= {"cmd", "keyring"}:
        if "cmd" in value:
            raw = subprocess.check_output(str(value["cmd"]), shell=True)
            return raw.decode("utf-8").strip()
        if "keyring" in value:
            from dokli.secrets import get_secret

            secret = get_secret(str(value["keyring"]))
            if secret is None:
                raise ValueError(f"No secret stored for '{value['keyring']}'.")
            return secret
    return value


class ResourceManager:
    """Applies generic manifest resources against a connection.

    Slice 1 covers leaf resources (domain, port, ...) hanging off a service
    declared in the manifest's typed ``projects``. Ancestors (project,
    environment, service) are resolved from the live state, honoring the
    ``in`` path.
    """

    def __init__(self, applier) -> None:
        """Construct the resource manager sharing the applier's client/report."""
        self.applier = applier
        self.manifest = applier.manifest
        self.client = applier.client
        self.report = applier.report
        self.state: State = applier._state
        self.registry = build_registry(self.client)

    def run(self, dry_run: bool = False) -> None:
        """Apply all generic resources."""
        for resource in self.manifest.resources:
            self._apply_resource(resource, dry_run)

    def _apply_resource(self, resource: Resource, dry_run: bool) -> None:
        segments = parse_in(resource.in_)
        if not segments:
            raise ValueError(f"Resource '{resource.kind}:{resource.name}' must declare its parent via 'in:'.")
        parent_kind, parent_name = segments[-1]
        if parent_kind not in SERVICE_KINDS:
            raise ValueError(
                f"Resource '{resource.kind}:{resource.name}' parent '{parent_kind}' is not supported yet."
            )
        allowed = PARENT_KINDS.get(resource.kind)
        if allowed is not None and parent_kind not in allowed:
            raise ValueError(
                f"Resource '{resource.kind}:{resource.name}' cannot hang off '{parent_kind}' "
                f"(allowed: {', '.join(sorted(allowed))})."
            )
        self._apply_service_child(resource, parent_kind, parent_name, segments[:-1], dry_run)

    def _apply_service_child(
        self,
        resource: Resource,
        parent_kind: str,
        parent_name: str,
        ancestors: list[tuple[str, str]],
        dry_run: bool,
    ) -> None:
        service = self._find_live_service(parent_kind, parent_name, ancestors)
        if service is None:
            # Record a validation action instead of aborting after a partial apply.
            self.report.actions.append(
                ApplyAction(
                    action="skip",
                    kind=resource.kind,
                    name=resource.name,
                    details=f"Parent service '{parent_kind}:{parent_name}' not found.",
                )
            )
            return
        record = self.client.request("GET", f"{parent_kind}.one", {f"{parent_kind}Id": service.service_id}).json()
        key = match_key(resource.kind)
        value = match_value(resource, key)
        children = fetch_children(self.client, resource.kind, parent_kind, service.service_id, record)
        child = next((c for c in children if str(c.get(key)) == value), None)

        parent_field = PARENT_ID_FIELDS.get(resource.kind, f"{parent_kind}Id")
        body = {**resolve_data(resource.data), parent_field: service.service_id}
        # Named references (e.g. backups -> destination) are resolved to ids.
        named_field = NAMED_REFERENCES.get(resource.kind)
        if named_field in body:
            body[f"{named_field}Id"] = self._resolve_named(named_field, str(body.pop(named_field)))
        # The match key only falls back to the resource name when the data omits
        # it; matching itself is string-based, but the payload keeps the data types.
        if key not in body:
            body[key] = self._coerce(resource.kind, key, resource.name)
        if resource.kind == "mount":
            body["serviceType"] = parent_kind

        entity = entity_name(resource.kind)
        if child is None:
            action = "create"
            if not dry_run:
                create_body = self._create_body(resource.kind, body)
                self.client.request("POST", f"{entity}.create", {"body": create_body})
        elif self._changed(child, body):
            action = "update"
            if not dry_run:
                update_body = self._update_body(resource, child, body)
                self.client.request("POST", f"{entity}.update", {"body": update_body})
        else:
            action = "skip"
        self.report.actions.append(ApplyAction(action=action, kind=resource.kind, name=resource.name))

    def _find_live_service(self, kind: str, name: str, ancestors: list[tuple[str, str]]):
        """Find a live service by kind + name, honoring the ancestor path.

        Returns None when not found; raises on ambiguity.
        """
        projects = self.state.projects
        for seg_kind, seg_name in ancestors:
            if seg_kind == "project":
                projects = [p for p in projects if p.name == seg_name]
            elif seg_kind == "environment":
                projects = [p for p in projects if seg_name in {e.name for e in p.environments}]
        matches = []
        for project in projects:
            for environment in project.environments:
                for service in environment.services:
                    if service.type == kind and service.name == name:
                        matches.append(service)
        if not matches:
            return None
        if len(matches) > 1:
            raise ValueError(f"Ambiguous parent service '{kind}:{name}' (matches multiple projects).")
        return matches[0]

    def _changed(self, live: dict, body: dict) -> bool:
        """Whether the live child differs from the desired body.

        Id fields (parents/entity) are excluded. Any desired field missing from
        the live record counts as a change so it gets set, not silently skipped.
        """
        for field, value in body.items():
            if field.endswith("Id"):
                continue
            if field not in live or str(live.get(field)) != str(value):
                return True
        return False

    def _create_body(self, kind: str, body: dict) -> dict:
        """Fill required create fields that have a schema default but are absent."""
        entity = self.registry.get(entity_name(kind))
        create = entity.get("create") if entity else None
        if create is None:
            return body
        props = create.request_schema.get("properties", {})
        filled = dict(body)
        for field in create.request_schema.get("required", []):
            if field not in filled:
                prop = props.get(field, {})
                if "default" in prop:
                    filled[field] = prop["default"]
        return filled

    def _update_body(self, resource: Resource, child: dict, body: dict) -> dict:
        """Build an update payload, merging the live child for full-object kinds.

        Kinds in ``UPDATE_MERGE_KINDS`` have required update fields that the
        create may not set; the live record supplies them (body wins, ids are
        re-added from the record).
        """
        entity_id = child[id_field(resource.kind)]
        merged = {**body, id_field(resource.kind): entity_id}
        if resource.kind not in UPDATE_MERGE_KINDS:
            return merged
        live = {key: value for key, value in child.items() if not key.endswith(("Id", "At"))}
        return {**live, **body, id_field(resource.kind): entity_id}

    def _resolve_named(self, entity: str, name: str) -> str:
        """Resolve a named reference (e.g. ``destination``) to its id."""
        raw = self.client.request("GET", f"{entity}.all", {}).json()
        items = raw if isinstance(raw, list) else raw.get("items", [])
        matches = [item for item in items if str(item.get("name")) == name]
        if not matches:
            raise ValueError(f"{entity} '{name}' not found in the instance.")
        if len(matches) > 1:
            raise ValueError(f"Ambiguous {entity} '{name}'.")
        entity_id = matches[0].get(f"{entity}Id")
        if not entity_id:
            raise ValueError(f"{entity} '{name}' has no id.")
        return str(entity_id)

    def _coerce(self, kind: str, field: str, value: str) -> Any:
        """Coerce a fallback match value to the schema type when numeric."""
        entity = self.registry.get(entity_name(kind))
        create = entity.get("create") if entity is not None else None
        schema = create.request_schema if create is not None else None
        if schema is None:
            update = entity.get("update") if entity is not None else None
            schema = update.request_schema if update is not None else None
        prop = (schema or {}).get("properties", {}).get(field, {})
        if prop.get("type") in ("number", "integer"):
            try:
                return int(value) if prop.get("type") == "integer" else float(value)
            except ValueError:
                return value
        return value
