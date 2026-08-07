"""Apply a manifest to a Dokploy instance (idempotent, additive).

Apply never deletes resources that are not in the manifest. Services are
created with the minimal payload the API requires, then fully updated to the
desired state (the API splits ``create`` and ``update`` inputs).
"""

import secrets
import subprocess
from typing import Any, Literal

from pydantic import BaseModel, Field

from dokli.api_client import APIClient
from dokli.config import ConnectionConfig
from dokli.diff import resolve_compose_file
from dokli.manifest import ApplicationService, ComposeService, DatabaseService, Manifest, Service
from dokli.secrets import db_account, get_secret
from dokli.state import LiveGitProvider, LiveProject, LiveService, State, collect_state


class ApplyAction(BaseModel):
    """A single apply action."""

    action: Literal["create", "update", "validate", "skip"]
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
    details: str = ""


class ApplyReport(BaseModel):
    """Report of what apply did or would do."""

    actions: list[ApplyAction] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class Applier:
    """Applies a manifest to a connection."""

    def __init__(self, manifest: Manifest, connection: ConnectionConfig, deploy: bool = False):
        """Initialize the applier with a manifest and connection."""
        self.manifest = manifest
        self.connection = connection
        self.client = APIClient(connection)
        self.deploy = deploy
        self.report = ApplyReport()
        self._live_providers: dict[str, LiveGitProvider] = {}
        self._state: State = State(connection="")

    def run(self, dry_run: bool = False) -> ApplyReport:
        """Apply the manifest, optionally only planning (dry_run)."""
        state = collect_state(self.connection, client=self.client)
        self._state = state
        self._live_providers = {provider.name: provider for provider in state.git_providers}
        self._validate_git_providers()

        live_projects = {project.name: project for project in state.projects}
        for project_def in self.manifest.projects:
            live_project = live_projects.get(project_def.name)
            if live_project is None:
                self._create_project(project_def, dry_run)
            else:
                self._apply_to_project(project_def, live_project, dry_run)

        return self.report

    def _validate_git_providers(self) -> None:
        for provider_def in self.manifest.git_providers:
            live = self._live_providers.get(provider_def.name)
            if live is None:
                self.report.actions.append(
                    ApplyAction(
                        action="validate",
                        kind="git_provider",
                        name=provider_def.name,
                        details="Git provider not found in the instance. Configure it manually.",
                    )
                )
            elif live.provider != provider_def.provider:
                self.report.actions.append(
                    ApplyAction(
                        action="validate",
                        kind="git_provider",
                        name=provider_def.name,
                        details=(
                            f"Type mismatch: manifest '{provider_def.provider}' " f"vs instance '{live.provider}'."
                        ),
                    )
                )
            elif not live.is_configured:
                self.report.actions.append(
                    ApplyAction(
                        action="validate",
                        kind="git_provider",
                        name=provider_def.name,
                        details="Git provider is not configured in the instance.",
                    )
                )

    def _create_project(self, project_def, dry_run: bool) -> None:
        if dry_run:
            self.report.actions.append(
                ApplyAction(action="create", kind="project", project=project_def.name, name=project_def.name)
            )
            self._plan_services(project_def, project_def.services)
            for env_def in project_def.environments:
                self.report.actions.append(
                    ApplyAction(action="create", kind="environment", project=project_def.name, name=env_def.name)
                )
                self._plan_services(project_def, env_def.services)
            return

        payload: dict[str, Any] = {"name": project_def.name}
        if project_def.description:
            payload["description"] = project_def.description
        response = self.client.request("POST", "project.create", {"body": payload}).json()
        default_environment_id = response["environment"]["environmentId"]
        project_id = response["project"]["projectId"]
        self.report.actions.append(
            ApplyAction(action="create", kind="project", project=project_def.name, name=project_def.name)
        )
        self._apply_services(project_def, project_def.services, default_environment_id)
        for env_def in project_def.environments:
            environment_id = self._create_environment(project_def.name, project_id, env_def.name, dry_run=False)
            if environment_id:
                self._apply_services(project_def, env_def.services, environment_id)

    def _apply_to_project(self, project_def, live_project: LiveProject, dry_run: bool) -> None:
        default_environment = next(
            (environment for environment in live_project.environments if environment.is_default),
            None,
        )
        if default_environment is None:
            self.report.actions.append(
                ApplyAction(
                    action="skip",
                    kind="project",
                    project=project_def.name,
                    name=project_def.name,
                    details="No default environment found.",
                )
            )
            return
        self._apply_services(project_def, project_def.services, default_environment.environment_id, dry_run)

        for env_def in project_def.environments:
            live_env = next(
                (environment for environment in live_project.environments if environment.name == env_def.name),
                None,
            )
            if live_env is None:
                environment_id = self._create_environment(
                    project_def.name, live_project.project_id, env_def.name, dry_run
                )
            else:
                environment_id = live_env.environment_id
            if environment_id:
                self._apply_services(project_def, env_def.services, environment_id, dry_run)

    def _apply_services(self, project_def, service_defs, environment_id: str, dry_run: bool = False) -> None:
        """Create or update a list of services within an environment."""
        live_services = self._live_services(project_def.name, environment_id)
        for service_def in service_defs:
            live_service = live_services.get(service_def.name)
            if live_service is None:
                self._create_service(project_def.name, service_def, environment_id, dry_run)
            else:
                self._update_service(project_def.name, service_def, live_service, dry_run)

    def _live_services(self, project_name: str, environment_id: str) -> dict[str, LiveService]:
        """Resolve live services for an environment id.

        Uses the state snapshot captured at the start of the run.
        """
        state = self._state
        for project in state.projects:
            if project.name != project_name:
                continue
            for environment in project.environments:
                if environment.environment_id == environment_id:
                    return {service.name: service for service in environment.services}
        return {}

    def _plan_services(self, project_def, service_defs) -> None:
        """Record create actions for services (dry-run helper)."""
        for service_def in service_defs:
            self.report.actions.append(
                ApplyAction(action="create", kind=service_def.type, project=project_def.name, name=service_def.name)
            )

    def _create_environment(self, project_name: str, project_id: str, env_name: str, dry_run: bool) -> str | None:
        """Ensure a named environment exists and return its id."""
        if dry_run:
            self.report.actions.append(
                ApplyAction(action="create", kind="environment", project=project_name, name=env_name)
            )
            return None
        payload = {"projectId": project_id, "name": env_name}
        response = self.client.request("POST", "environment.create", {"body": payload}).json()
        self.report.actions.append(
            ApplyAction(action="create", kind="environment", project=project_name, name=env_name)
        )
        return response["environmentId"]

    def _create_service(self, project_name: str, service_def: Service, environment_id: str, dry_run: bool) -> None:
        if dry_run:
            self.report.actions.append(
                ApplyAction(action="create", kind=service_def.type, project=project_name, name=service_def.name)
            )
            return
        try:
            if isinstance(service_def, ComposeService):
                service_id = self._create_compose(service_def, environment_id)
            elif isinstance(service_def, ApplicationService):
                service_id = self._create_application(service_def, environment_id)
            else:
                service_id = self._create_database(service_def, environment_id)
            payload = self._service_desired_payload(service_def, None)
            self._apply_update(service_def.type, service_id, payload)
        except ValueError as err:
            self.report.actions.append(
                ApplyAction(
                    action="skip",
                    kind=service_def.type,
                    project=project_name,
                    name=service_def.name,
                    details=str(err),
                )
            )
            return
        self.report.actions.append(
            ApplyAction(action="create", kind=service_def.type, project=project_name, name=service_def.name)
        )
        if self.deploy:
            self._deploy(service_def.type, service_id)

    def _update_service(
        self, project_name: str, service_def: Service, live_service: LiveService, dry_run: bool
    ) -> None:
        try:
            payload = self._service_desired_payload(service_def, live_service)
        except ValueError as err:
            self.report.actions.append(
                ApplyAction(
                    action="skip",
                    kind=service_def.type,
                    project=project_name,
                    name=service_def.name,
                    details=str(err),
                )
            )
            return
        if not payload:
            return
        if dry_run:
            self.report.actions.append(
                ApplyAction(
                    action="update",
                    kind=service_def.type,
                    project=project_name,
                    name=service_def.name,
                    details=", ".join(sorted(payload)),
                )
            )
            return
        self._apply_update(service_def.type, live_service.service_id, payload)
        self.report.actions.append(
            ApplyAction(action="update", kind=service_def.type, project=project_name, name=service_def.name)
        )
        if self.deploy:
            self._deploy(service_def.type, live_service.service_id)

    def _create_compose(self, service_def: ComposeService, environment_id: str) -> str:
        payload: dict[str, Any] = {
            "name": service_def.name,
            "environmentId": environment_id,
            "composeType": "docker-compose",
        }
        if service_def.description:
            payload["description"] = service_def.description
        response = self.client.request("POST", "compose.create", {"body": payload}).json()
        return response["composeId"]

    def _create_application(self, service_def: ApplicationService, environment_id: str) -> str:
        payload: dict[str, Any] = {
            "name": service_def.name,
            "environmentId": environment_id,
        }
        if service_def.description:
            payload["description"] = service_def.description
        response = self.client.request("POST", "application.create", {"body": payload}).json()
        return response["applicationId"]

    def _create_database(self, service_def: DatabaseService, environment_id: str) -> str:
        password = self._resolve_database_password(service_def)
        payload: dict[str, Any] = {
            "name": service_def.name,
            "environmentId": environment_id,
            "databasePassword": password,
        }
        if service_def.type != "redis":
            payload["databaseUser"] = service_def.database_user or service_def.name
        if service_def.type in ("postgres", "mysql", "mariadb"):
            payload["databaseName"] = service_def.database_name or service_def.name
        if service_def.description:
            payload["description"] = service_def.description
        if service_def.image:
            payload["dockerImage"] = service_def.image
        response = self.client.request("POST", f"{service_def.type}.create", {"body": payload}).json()
        return response[f"{service_def.type}Id"]

    def _resolve_database_password(self, service_def: DatabaseService) -> str:
        """Resolve a database password from the manifest (or generate one)."""
        if service_def.password:
            return service_def.password
        if service_def.password_keyring:
            value = get_secret(db_account(service_def.name))
            if value:
                return value
        if service_def.password_cmd:
            output = subprocess.check_output(service_def.password_cmd, shell=True)
            return output.decode("utf-8").strip()
        generated = secrets.token_urlsafe(24)
        self.report.warnings.append(
            f"Database '{service_def.name}': no password/password_cmd set, "
            f"generated a random password (not stored): {generated}"
        )
        return generated

    def _apply_update(self, service_type: str, service_id: str, payload: dict[str, Any]) -> None:
        if not payload:
            return
        id_field = f"{service_type}Id"
        payload[id_field] = service_id
        self.client.request("POST", f"{service_type}.update", {"body": payload})

    def _deploy(self, service_type: str, service_id: str) -> None:
        id_field = f"{service_type}Id"
        self.client.request("POST", f"{service_type}.deploy", {"body": {id_field: service_id}})

    def _service_desired_payload(self, service_def: Service, live: LiveService | None) -> dict[str, Any]:
        """Return the desired fields for a service, skipping fields that already match."""
        if isinstance(service_def, ComposeService):
            return self._compose_payload(service_def, live)
        if isinstance(service_def, ApplicationService):
            return self._application_payload(service_def, live)
        return self._database_payload(service_def, live)

    def _compose_payload(self, service_def: ComposeService, live: LiveService | None) -> dict[str, Any]:
        payload: dict[str, Any] = {}
        if service_def.description is not None and (
            live is None or (live.description or "") != service_def.description
        ):
            payload["description"] = service_def.description
        if service_def.source:
            provider_type, subtype_id = self._resolve_provider(service_def.source.provider)
            if live is None or live.source_type != provider_type or live.provider != service_def.source.provider:
                payload["sourceType"] = provider_type
                payload[f"{provider_type}Id"] = subtype_id
            owner, _, repository = service_def.source.repository.partition("/")
            if live is None or live.owner != owner:
                payload["owner"] = owner
            if live is None or live.repository != repository:
                payload["repository"] = repository
            if live is None or live.branch != service_def.source.branch:
                payload["branch"] = service_def.source.branch
            if service_def.compose_path and (live is None or live.compose_path != service_def.compose_path):
                payload["composePath"] = service_def.compose_path
        elif service_def.compose_file:
            content = resolve_compose_file(service_def.compose_file)
            if live is None or (live.compose_file or "") != content:
                payload["composeFile"] = content
                payload["sourceType"] = "raw"
        if service_def.command is not None and (live is None or (live.command or "") != service_def.command):
            payload["command"] = service_def.command
        if service_def.env is not None and (live is None or (live.env or "") != service_def.env):
            payload["env"] = service_def.env
        return payload

    def _application_payload(self, service_def: ApplicationService, live: LiveService | None) -> dict[str, Any]:
        payload: dict[str, Any] = {}
        if service_def.description is not None and (
            live is None or (live.description or "") != service_def.description
        ):
            payload["description"] = service_def.description
        if service_def.source:
            provider_type, subtype_id = self._resolve_provider(service_def.source.provider)
            if live is None or live.source_type != provider_type or live.provider != service_def.source.provider:
                payload["sourceType"] = provider_type
                payload[f"{provider_type}Id"] = subtype_id
            owner, _, repository = service_def.source.repository.partition("/")
            if live is None or live.owner != owner:
                payload["owner"] = owner
            if live is None or live.repository != repository:
                payload["repository"] = repository
            if live is None or live.branch != service_def.source.branch:
                payload["branch"] = service_def.source.branch
        elif service_def.image and (live is None or live.docker_image != service_def.image):
            payload["sourceType"] = "docker"
            payload["dockerImage"] = service_def.image
        if service_def.build_type and (live is None or live.build_type != service_def.build_type):
            payload["buildType"] = service_def.build_type
        if service_def.dockerfile_location and (
            live is None or live.dockerfile_location != service_def.dockerfile_location
        ):
            payload["dockerfileLocation"] = service_def.dockerfile_location
        if service_def.build_path and (live is None or live.build_path != service_def.build_path):
            payload["buildPath"] = service_def.build_path
        if service_def.env is not None and (live is None or (live.env or "") != service_def.env):
            payload["env"] = service_def.env
        return payload

    def _database_payload(self, service_def: DatabaseService, live: LiveService | None) -> dict[str, Any]:
        payload: dict[str, Any] = {}
        if service_def.description is not None and (
            live is None or (live.description or "") != service_def.description
        ):
            payload["description"] = service_def.description
        if service_def.image and (live is None or live.docker_image != service_def.image):
            payload["dockerImage"] = service_def.image
        if service_def.type in ("postgres", "mysql", "mariadb"):
            database_name = service_def.database_name or service_def.name
            if live is None or live.database_name != database_name:
                payload["databaseName"] = database_name
        if service_def.type != "redis":
            database_user = service_def.database_user or service_def.name
            if live is None or live.database_user != database_user:
                payload["databaseUser"] = database_user
        if service_def.password or service_def.password_keyring or service_def.password_cmd:
            password = self._resolve_database_password(service_def)
            if live is None or live.database_password != password:
                payload["databasePassword"] = password
        if service_def.env is not None and (live is None or (live.env or "") != service_def.env):
            payload["env"] = service_def.env
        return payload

    def _resolve_provider(self, name: str) -> tuple[str, str]:
        """Resolve a manifest provider name to (provider type, subtype id)."""
        provider_def = self.manifest.get_git_provider(name)
        live = self._live_providers.get(name)
        if live is None:
            raise ValueError(f"Git provider '{name}' is not configured in the instance.")
        if live.provider != provider_def.provider:
            raise ValueError(
                f"Git provider '{name}' type mismatch: manifest '{provider_def.provider}' "
                f"vs instance '{live.provider}'."
            )
        if not live.is_configured:
            raise ValueError(f"Git provider '{name}' is not configured in the instance.")
        subtype_id = getattr(live, f"{provider_def.provider}_id")
        if not subtype_id:
            raise ValueError(f"Git provider '{name}' has no {provider_def.provider} credential.")
        return provider_def.provider, subtype_id
