"""Generic schema-driven resources (issue #50).

A generic manifest resource (``kind`` + ``name`` + ``in`` + ``data``) is
resolved against the entity registry and the live instance. The schema
conventions are followed by default; the curated maps below cover the known
historical exceptions (kinds without a stable ``name``, parents addressed via
``serviceId`` instead of ``<parent>Id``).
"""

import subprocess
from typing import TYPE_CHECKING, Any

from dokli.manifest import Resource
from dokli.report import ApplyAction
from dokli.tui.engine.spec import NESTED_CHILD_KEYS

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

# Child kind -> the nested array key on the parent service record.
CHILD_ARRAY: dict[str, str] = {child: key for key, child in NESTED_CHILD_KEYS.items()}

# Service kinds that can host leaf resources.
SERVICE_KINDS = frozenset(
    {"compose", "application", "postgres", "mysql", "mariadb", "mongo", "redis", "libsql"}
)


def match_key(kind: str) -> str:
    """The field used to match a resource kind against the live instance."""
    return MATCH_KEYS.get(kind, "name")


def child_array_key(kind: str) -> str:
    """The nested array key of a child kind on the parent service record."""
    try:
        return CHILD_ARRAY[kind]
    except KeyError:
        raise ValueError(f"Kind '{kind}' is not a known child resource.") from None


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
    environment, service) are resolved from the live state.
    """

    def __init__(self, applier) -> None:
        """Construct the resource manager sharing the applier's client/report."""
        self.applier = applier
        self.manifest = applier.manifest
        self.client = applier.client
        self.report = applier.report
        self.state: State = applier._state

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
        self._apply_service_child(resource, parent_kind, parent_name, dry_run)

    def _apply_service_child(self, resource: Resource, parent_kind: str, parent_name: str, dry_run: bool) -> None:
        service = self._find_live_service(parent_kind, parent_name)
        if service is None:
            raise ValueError(
                f"Parent service '{parent_kind}:{parent_name}' not found in the instance "
                "(declare it in 'projects:' so it is created first)."
            )
        record = self.client.request("GET", f"{parent_kind}.one", {f"{parent_kind}Id": service.service_id}).json()
        key = match_key(resource.kind)
        value = match_value(resource, key)
        children = record.get(child_array_key(resource.kind)) or []
        child = next((c for c in children if str(c.get(key)) == value), None)

        parent_field = "serviceId" if resource.kind == "mount" else f"{parent_kind}Id"
        body = {**resolve_data(resource.data), parent_field: service.service_id, key: value}
        if resource.kind == "mount":
            body["serviceType"] = parent_kind

        if child is None:
            action = "create"
            if not dry_run:
                self.client.request("POST", f"{resource.kind}.create", {"body": body})
        elif self._changed(child, body):
            action = "update"
            if not dry_run:
                entity_id = child[f"{resource.kind}Id"]
                update_body = {**body, f"{resource.kind}Id": entity_id}
                self.client.request("POST", f"{resource.kind}.update", {"body": update_body})
        else:
            action = "skip"
        self.report.actions.append(
            ApplyAction(action=action, kind=resource.kind, name=resource.name)
        )

    def _find_live_service(self, kind: str, name: str):
        """Find a live service by kind + name, or None (error on ambiguity)."""
        matches = []
        for project in self.state.projects:
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

        Only fields present on the live record are compared (parent ids and
        read-only fields are excluded).
        """
        return any(live.get(field) != value for field, value in body.items() if field in live)
