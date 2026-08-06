"""Typed reads of the live state of a Dokploy instance.

The state collector normalizes the raw API responses into typed models so that
downstream features (``plan``, ``apply``, ``export``) can work symmetrically
with the manifest models in :mod:`dokli.manifest`.
"""

from typing import Any, Literal

from pydantic import BaseModel, Field

from dokli.api_client import APIClient
from dokli.config import ConnectionConfig


class LiveService(BaseModel):
    """A service as it exists in the instance."""

    service_id: str
    app_name: str
    type: Literal[
        "compose",
        "application",
        "postgres",
        "mysql",
        "mariadb",
        "mongo",
        "redis",
    ]
    name: str
    description: str | None = None
    source_type: str | None = None
    provider: str | None = Field(default=None, description="Git provider name (resolved).")
    repository: str | None = None
    owner: str | None = None
    branch: str | None = None
    build_type: str | None = None
    dockerfile_location: str | None = None
    docker_image: str | None = None
    build_path: str | None = None
    compose_path: str | None = None
    compose_file: str | None = None
    command: str | None = None
    database_name: str | None = None
    database_user: str | None = None
    database_password: str | None = None
    env: str | None = None
    server_id: str | None = None


class LiveEnvironment(BaseModel):
    """An environment within a project."""

    environment_id: str
    name: str
    is_default: bool
    services: list[LiveService] = Field(default_factory=list)


class LiveProject(BaseModel):
    """A project as it exists in the instance."""

    project_id: str
    name: str
    description: str | None = None
    environments: list[LiveEnvironment] = Field(default_factory=list)


class LiveGitProvider(BaseModel):
    """A git provider as it exists in the instance (credentials are write-only)."""

    git_provider_id: str
    name: str
    provider: str
    url: str | None = None
    app_name: str | None = None
    is_configured: bool
    github_id: str | None = None
    gitlab_id: str | None = None
    gitea_id: str | None = None
    bitbucket_id: str | None = None


class LiveServer(BaseModel):
    """A server (deployment node) in the instance."""

    server_id: str
    name: str


class State(BaseModel):
    """Normalized live state of a connection."""

    connection: str
    projects: list[LiveProject] = Field(default_factory=list)
    git_providers: list[LiveGitProvider] = Field(default_factory=list)
    servers: list[LiveServer] = Field(default_factory=list)


def collect_state(connection: ConnectionConfig, client: APIClient | None = None) -> State:
    """Collect the live state of a connection."""
    client = client or APIClient(connection)
    raw_projects = client.request("GET", "project.all", {}).json()
    raw_providers = client.request("GET", "gitProvider.getAll", {}).json()
    raw_servers = client.request("GET", "server.all", {}).json()

    provider_map = _build_provider_map(raw_providers)

    projects = [_collect_project(client, raw_project, provider_map) for raw_project in raw_projects]

    return State(
        connection=connection.name,
        projects=projects,
        git_providers=[_collect_git_provider(raw) for raw in raw_providers],
        servers=[_collect_server(raw) for raw in raw_servers],
    )


def _collect_project(client: APIClient, raw_project: dict[str, Any], provider_map: dict[str, str]) -> LiveProject:
    detail = client.request("GET", "project.one", {"projectId": raw_project["projectId"]}).json()
    environments = [
        LiveEnvironment(
            environment_id=environment["environmentId"],
            name=environment.get("name") or "",
            is_default=environment.get("isDefault", False),
            services=[
                *_collect_services("compose", environment.get("compose", []), provider_map),
                *_collect_services("application", environment.get("applications", []), provider_map),
                *_collect_services("postgres", environment.get("postgres", []), provider_map),
                *_collect_services("mysql", environment.get("mysql", []), provider_map),
                *_collect_services("mariadb", environment.get("mariadb", []), provider_map),
                *_collect_services("mongo", environment.get("mongo", []), provider_map),
                *_collect_services("redis", environment.get("redis", []), provider_map),
            ],
        )
        for environment in detail.get("environments", [])
    ]
    return LiveProject(
        project_id=detail["projectId"],
        name=detail.get("name") or "",
        description=detail.get("description"),
        environments=environments,
    )


def _collect_services(
    service_type: str,
    raw_services: list[dict[str, Any]],
    provider_map: dict[str, str],
) -> list[LiveService]:
    services = []
    for raw in raw_services:
        service_id = _service_id(raw)
        if not service_id:
            continue
        services.append(
            LiveService(
                service_id=service_id,
                app_name=raw.get("appName") or "",
                type=service_type,  # type: ignore[arg-type]
                name=raw.get("name") or "",
                description=raw.get("description"),
                source_type=raw.get("sourceType"),
                provider=_resolve_provider(raw, provider_map),
                repository=_first(raw, "repository", "gitlabRepository", "giteaRepository", "bitbucketRepository"),
                owner=_first(raw, "owner", "gitlabOwner", "giteaOwner", "bitbucketOwner"),
                branch=_first(raw, "branch", "gitlabBranch", "giteaBranch", "bitbucketBranch"),
                build_type=raw.get("buildType"),
                dockerfile_location=raw.get("dockerfileLocation"),
                docker_image=raw.get("dockerImage"),
                build_path=raw.get("buildPath"),
                compose_path=raw.get("composePath"),
                compose_file=raw.get("composeFile"),
                command=raw.get("command"),
                database_name=raw.get("databaseName"),
                database_user=raw.get("databaseUser"),
                database_password=raw.get("databasePassword"),
                env=raw.get("env"),
                server_id=raw.get("serverId"),
            )
        )
    return services


def _collect_git_provider(raw: dict[str, Any]) -> LiveGitProvider:
    subprovider = _first(raw, "github", "gitlab", "gitea", "bitbucket")
    return LiveGitProvider(
        git_provider_id=raw["gitProviderId"],
        name=raw.get("name") or raw["gitProviderId"],
        provider=raw.get("providerType") or "",
        url=subprovider.get("url") if isinstance(subprovider, dict) else None,
        app_name=subprovider.get("appName") if isinstance(subprovider, dict) else None,
        is_configured=bool(raw.get("isConfigured"))
        or (isinstance(subprovider, dict) and bool(subprovider.get("isConfigured"))),
        github_id=(raw.get("github") or {}).get("githubId"),
        gitlab_id=(raw.get("gitlab") or {}).get("gitlabId"),
        gitea_id=(raw.get("gitea") or {}).get("giteaId"),
        bitbucket_id=(raw.get("bitbucket") or {}).get("bitbucketId"),
    )


def _collect_server(raw: dict[str, Any]) -> LiveServer:
    return LiveServer(server_id=raw["serverId"], name=raw.get("name") or raw["serverId"])


def _build_provider_map(raw_providers: list[dict[str, Any]]) -> dict[str, str]:
    """Map subtype id (githubId, ...) to provider name."""
    mapping: dict[str, str] = {}
    for raw in raw_providers:
        name = raw.get("name")
        if not name:
            continue
        for key in ("github", "gitlab", "gitea", "bitbucket"):
            subtype = raw.get(key) or {}
            subtype_id = subtype.get(f"{key}Id")
            if subtype_id:
                mapping[subtype_id] = name
    return mapping


def _resolve_provider(raw: dict[str, Any], provider_map: dict[str, str]) -> str | None:
    for key in ("githubId", "gitlabId", "giteaId", "bitbucketId"):
        subtype_id = raw.get(key)
        if subtype_id:
            return provider_map.get(subtype_id)
    return None


def _first(mapping: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if mapping.get(key) is not None:
            return mapping[key]
    return None


def _service_id(raw: dict[str, Any]) -> str | None:
    for key in (
        "composeId",
        "applicationId",
        "postgresId",
        "mysqlId",
        "mariadbId",
        "mongoId",
        "redisId",
    ):
        if raw.get(key):
            return raw[key]
    return None
