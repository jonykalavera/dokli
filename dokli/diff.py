"""Declarative diff between a manifest and the live state of an instance."""

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

from dokli.manifest import ApplicationService, ComposeService, DatabaseService, GitSource, Manifest, Service
from dokli.resources import env_changed, resolve_env
from dokli.state import LiveEnvironment, LiveProject, LiveService, State


class PlanItem(BaseModel):
    """A single planned change."""

    action: Literal["create", "update", "validate"]
    kind: Literal[
        "project",
        "environment",
        "compose",
        "application",
        "postgres",
        "mysql",
        "mariadb",
        "mongo",
        "redis",
        "git_provider",
    ]
    project: str = ""
    name: str
    changed: list[str] = Field(default_factory=list)
    reason: str = ""


class Plan(BaseModel):
    """The diff between a manifest and the live state."""

    connection: str
    items: list[PlanItem] = Field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        """Whether any change is planned."""
        return bool(self.items)


def build_plan(manifest: Manifest, state: State) -> Plan:
    """Build a plan comparing the manifest against the live state."""
    items: list[PlanItem] = []
    live_projects = {project.name: project for project in state.projects}

    for project_def in manifest.projects:
        live_project = live_projects.get(project_def.name)
        if live_project is None:
            items.append(
                PlanItem(
                    action="create",
                    kind="project",
                    project=project_def.name,
                    name=project_def.name,
                    reason="Project does not exist.",
                )
            )
            for service_def in project_def.services:
                items.append(
                    PlanItem(
                        action="create",
                        kind=service_def.type,
                        project=project_def.name,
                        name=service_def.name,
                        reason="Service will be created with the project.",
                    )
                )
            for env_def in project_def.environments:
                items.append(
                    PlanItem(
                        action="create",
                        kind="environment",
                        project=project_def.name,
                        name=env_def.name,
                        reason="Environment will be created with the project.",
                    )
                )
                for service_def in env_def.services:
                    items.append(
                        PlanItem(
                            action="create",
                            kind=service_def.type,
                            project=project_def.name,
                            name=service_def.name,
                            reason="Service will be created with the environment.",
                        )
                    )
            continue

        default_environment = _default_environment(live_project)
        _plan_services(
            project_def,
            project_def.services,
            default_environment.services if default_environment else [],
            items,
        )

        for env_def in project_def.environments:
            live_env = next(
                (environment for environment in live_project.environments if environment.name == env_def.name),
                None,
            )
            if live_env is None:
                items.append(
                    PlanItem(
                        action="create",
                        kind="environment",
                        project=project_def.name,
                        name=env_def.name,
                        reason="Environment does not exist.",
                    )
                )
                for service_def in env_def.services:
                    items.append(
                        PlanItem(
                            action="create",
                            kind=service_def.type,
                            project=project_def.name,
                            name=service_def.name,
                            reason="Service will be created with the environment.",
                        )
                    )
            else:
                _plan_services(project_def, env_def.services, live_env.services, items)

    _plan_git_providers(manifest, state, items)

    return Plan(connection=state.connection, items=items)


def _plan_services(project_def, service_defs, live_services, items: list[PlanItem]) -> None:
    """Plan services of one environment against its live services."""
    live = {service.name: service for service in live_services}
    for service_def in service_defs:
        live_service = live.get(service_def.name)
        if live_service is None:
            items.append(
                PlanItem(
                    action="create",
                    kind=service_def.type,
                    project=project_def.name,
                    name=service_def.name,
                    reason="Service does not exist.",
                )
            )
        else:
            changed = _service_changes(service_def, live_service)
            if changed:
                items.append(
                    PlanItem(
                        action="update",
                        kind=service_def.type,
                        project=project_def.name,
                        name=service_def.name,
                        changed=changed,
                    )
                )


def _plan_git_providers(manifest: Manifest, state: State, items: list[PlanItem]) -> None:
    live_providers = {provider.name: provider for provider in state.git_providers}
    for provider_def in manifest.git_providers:
        live_provider = live_providers.get(provider_def.name)
        if live_provider is None:
            items.append(
                PlanItem(
                    action="validate",
                    kind="git_provider",
                    name=provider_def.name,
                    reason="Git provider not found. It cannot be created via the API; configure it in the instance.",
                )
            )
        elif live_provider.provider != provider_def.provider:
            items.append(
                PlanItem(
                    action="validate",
                    kind="git_provider",
                    name=provider_def.name,
                    reason=(
                        f"Provider type mismatch: manifest '{provider_def.provider}' "
                        f"vs instance '{live_provider.provider}'."
                    ),
                )
            )
        elif not live_provider.is_configured:
            items.append(
                PlanItem(
                    action="validate",
                    kind="git_provider",
                    name=provider_def.name,
                    reason="Git provider is not configured.",
                )
            )


def _default_environment(project: LiveProject) -> LiveEnvironment | None:
    return next((environment for environment in project.environments if environment.is_default), None)


def _service_changes(service_def: Service, live: LiveService) -> list[str]:
    changes: list[str] = []
    if isinstance(service_def, ComposeService):
        _compose_changes(service_def, live, changes)
    elif isinstance(service_def, ApplicationService):
        _application_changes(service_def, live, changes)
    else:
        _database_changes(service_def, live, changes)
    return changes


def _compose_changes(service_def: ComposeService, live: LiveService, changes: list[str]) -> None:
    if service_def.description is not None and (live.description or "") != service_def.description:
        changes.append("description")
    if service_def.source:
        if _source_changed(service_def.source, live):
            changes.append("source")
        if service_def.compose_path and live.compose_path != service_def.compose_path:
            changes.append("compose_path")
    elif service_def.compose_file:
        if (live.compose_file or "") != resolve_compose_file(service_def.compose_file):
            changes.append("compose_file")
    if service_def.command is not None and (live.command or "") != service_def.command:
        changes.append("command")
    if service_def.env is not None and env_changed(resolve_env(service_def.env), live.env):
        changes.append("env")


def _application_changes(service_def: ApplicationService, live: LiveService, changes: list[str]) -> None:
    if service_def.description is not None and (live.description or "") != service_def.description:
        changes.append("description")
    if service_def.source:
        if _source_changed(service_def.source, live):
            changes.append("source")
    elif service_def.image and live.docker_image != service_def.image:
        changes.append("image")
    if service_def.build_type and live.build_type != service_def.build_type:
        changes.append("build_type")
    if service_def.dockerfile_location and live.dockerfile_location != service_def.dockerfile_location:
        changes.append("dockerfile_location")
    if service_def.build_path and live.build_path != service_def.build_path:
        changes.append("build_path")
    if service_def.env is not None and env_changed(resolve_env(service_def.env), live.env):
        changes.append("env")


def _database_changes(service_def: DatabaseService, live: LiveService, changes: list[str]) -> None:
    if service_def.description is not None and (live.description or "") != service_def.description:
        changes.append("description")
    if service_def.image and live.docker_image != service_def.image:
        changes.append("image")
    if service_def.database_name and live.database_name != service_def.database_name:
        changes.append("database_name")
    if service_def.database_user and live.database_user != service_def.database_user:
        changes.append("database_user")
    if service_def.password and live.database_password != service_def.password:
        changes.append("password")
    if service_def.env is not None and env_changed(resolve_env(service_def.env), live.env):
        changes.append("env")


def _source_changed(source: GitSource, live: LiveService) -> bool:
    """Compare a manifest source with a live service."""
    if live.source_type != source.provider:
        return True
    if live.provider != source.provider:
        return True
    owner, _, repository = source.repository.partition("/")
    if repository and live.repository != repository:
        return True
    if owner and live.owner != owner:
        return True
    return live.branch != source.branch


def resolve_compose_file(value: str) -> str:
    """Return compose YAML content, reading from disk when the value is a path."""
    path = Path(value)
    try:
        is_file = path.is_file()
    except OSError:
        return value
    if is_file:
        return path.read_text()
    return value
