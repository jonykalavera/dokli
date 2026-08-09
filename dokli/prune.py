"""Destructive reconciliation (issue #49).

``apply --prune`` deletes, within projects declared in the manifest, any child
record or service that is not described there. Projects and environments not in
the manifest are never touched.
"""

from collections import defaultdict
from typing import TYPE_CHECKING, Any

from dokli.report import ApplyAction
from dokli.resources import (
    EXPORT_FIELDS,
    PARENT_KINDS,
    ResourceManager,
    delete_spec,
    fetch_children,
    match_key,
    match_value,
    parse_in,
)

if TYPE_CHECKING:
    from dokli.manifest import Manifest

from dokli.tui.engine.spec import EntityRegistry


class Pruner:
    """Deletes live resources/services not described in the manifest."""

    def __init__(self, applier, registry: EntityRegistry) -> None:
        """Construct the pruner sharing the applier's client/report/state."""
        self.applier = applier
        self.client = applier.client
        self.manifest: Manifest = applier.manifest
        self.report = applier.report
        self.state = applier._state
        self.registry = registry
        self._resource_manager = ResourceManager(applier)
        self._desired_children: dict[tuple[str, str], set[str]] = defaultdict(set)

    def run(self, dry_run: bool = False) -> None:
        """Record delete actions for resources/services not in the manifest."""
        self._index_desired_children()
        for project_def in self.manifest.projects:
            live_project = next((p for p in self.state.projects if p.name == project_def.name), None)
            if live_project is None:
                continue
            self._prune_project(project_def, live_project, dry_run)

    def _index_desired_children(self) -> None:
        """Map (service id, kind) -> set of desired match values from resources."""
        for resource in self.manifest.resources:
            segments = parse_in(resource.in_)
            if not segments:
                continue
            parent_kind, parent_name = segments[-1]
            service = self._resource_manager._find_live_service(parent_kind, parent_name, segments[:-1])
            if service is None:
                continue
            key = match_key(resource.kind)
            self._desired_children[(service.service_id, resource.kind)].add(match_value(resource, key))

    def _prune_project(self, project_def, live_project, dry_run: bool) -> None:
        default_environment = next((e for e in live_project.environments if e.is_default), None)
        if default_environment is not None:
            desired = {service.name for service in project_def.services}
            for service in default_environment.services:
                if service.name not in desired:
                    self._delete_service(service, dry_run)
            for service_def in project_def.services:
                live = next((s for s in default_environment.services if s.name == service_def.name), None)
                if live is not None:
                    self._prune_service_children(live, dry_run)
        for environment_def in project_def.environments:
            live_environment = next((e for e in live_project.environments if e.name == environment_def.name), None)
            if live_environment is None:
                continue
            desired = {service.name for service in environment_def.services}
            for service in live_environment.services:
                if service.name not in desired:
                    self._delete_service(service, dry_run)
            for service_def in environment_def.services:
                live = next((s for s in live_environment.services if s.name == service_def.name), None)
                if live is not None:
                    self._prune_service_children(live, dry_run)

    def _prune_service_children(self, live_service, dry_run: bool) -> None:
        record = self.client.request(
            "GET", f"{live_service.type}.one", {f"{live_service.type}Id": live_service.service_id}
        ).json()
        for kind in EXPORT_FIELDS:
            allowed = PARENT_KINDS.get(kind)
            if allowed is not None and live_service.type not in allowed:
                continue
            desired = self._desired_children[(live_service.service_id, kind)]
            key = match_key(kind)
            for child in fetch_children(self.client, kind, live_service.type, live_service.service_id, record):
                if str(child.get(key)) in desired:
                    continue
                self._delete(kind, child, dry_run, label=child.get(key))

    def _delete_service(self, live_service, dry_run: bool) -> None:
        self._delete(
            live_service.type,
            {f"{live_service.type}Id": live_service.service_id},
            dry_run,
            label=live_service.name,
        )

    def _delete(self, kind: str, record: dict, dry_run: bool, label: Any = None) -> None:
        spec = delete_spec(self.registry, kind)
        if spec is None:
            self.report.actions.append(
                ApplyAction(action="skip", kind=kind, name="", details=f"No delete route for '{kind}'.")
            )
            return
        route, id_field, defaults = spec
        name = str(label or record.get("name") or record.get(id_field) or "")
        self.report.actions.append(ApplyAction(action="delete", kind=kind, name=name))
        if not dry_run:
            body = {**defaults, id_field: record[id_field]}
            self.client.request("POST", route, {"body": body})
