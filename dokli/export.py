"""Reverse-engineer a live Dokploy instance into a declarative manifest.

Git provider credentials are write-only in Dokploy's API, so exported providers
only carry metadata. The export returns warnings listing providers whose
credentials must be re-provided (via ``token_cmd``) for ``apply`` to succeed.
"""

from dokli.config import ConnectionConfig
from dokli.manifest import (
    ApplicationService,
    ComposeService,
    DatabaseService,
    EnvironmentDef,
    GitProvider,
    GitSource,
    Manifest,
    ProjectDef,
    Service,
)
from dokli.state import LiveService, State, collect_state

SUPPORTED_PROVIDERS: set[str] = {"github", "gitlab", "gitea", "bitbucket"}


def export_manifest(connection: ConnectionConfig, include_secrets: bool = False) -> tuple[Manifest, list[str]]:
    """Export a connection's live state into a manifest plus warnings.

    Environment variables are considered secrets and are redacted unless
    ``include_secrets`` is set. Git provider credentials are write-only and
    never exported.
    """
    state = collect_state(connection)
    warnings: list[str] = []

    git_providers = _export_git_providers(state, warnings)
    projects = [_export_project(project, include_secrets, warnings) for project in state.projects]

    return Manifest(
        connection=connection.name,
        git_providers=git_providers,
        projects=projects,
    ), warnings


def _export_git_providers(state: State, warnings: list[str]) -> list[GitProvider]:
    providers = []
    for provider in state.git_providers:
        if provider.provider not in SUPPORTED_PROVIDERS:
            warnings.append(f"Git provider '{provider.name}': unsupported type '{provider.provider}', skipping.")
            continue
        kwargs: dict = {
            "name": provider.name,
            "provider": provider.provider,  # type: ignore[arg-type]
            "app_name": provider.app_name,
            "owner": None,
            "token_cmd": None,
        }
        if provider.url:
            kwargs["url"] = provider.url
        providers.append(GitProvider(**kwargs))
        warnings.append(
            f"Git provider '{provider.name}': credentials are write-only, "
            "add token_cmd to the manifest so apply can resolve them."
        )
    return providers


def _export_project(project, include_secrets: bool, warnings: list[str]) -> ProjectDef:
    default_environment = next(
        (environment for environment in project.environments if environment.is_default),
        None,
    )
    default_services: list[Service] = []
    if default_environment is not None:
        default_services = [
            service
            for live in default_environment.services
            if (service := _export_service(live, include_secrets, warnings)) is not None
        ]
    environments = [
        EnvironmentDef(
            name=environment.name,
            services=[
                service
                for live in environment.services
                if (service := _export_service(live, include_secrets, warnings)) is not None
            ],
        )
        for environment in project.environments
        if not environment.is_default and environment.services
    ]
    return ProjectDef(
        name=project.name,
        description=project.description or None,
        services=default_services,
        environments=environments,
    )


def _export_service(live: LiveService, include_secrets: bool, warnings: list[str]) -> Service | None:
    if live.type == "compose":
        return _export_compose(live, include_secrets, warnings)
    if live.type == "application":
        return _export_application(live, include_secrets, warnings)
    return _export_database(live, include_secrets, warnings)


def _redact_env(live: LiveService, include_secrets: bool, warnings: list[str]) -> str | None:
    if not live.env:
        return None
    if include_secrets:
        return live.env
    warnings.append(
        f"Environment variables of '{live.name}' were redacted. " "Re-run with --include-secrets to export them."
    )
    return None


def _export_compose(live: LiveService, include_secrets: bool, warnings: list[str]) -> ComposeService:
    source = None
    compose_file = None
    compose_path = None
    if live.source_type == "raw":
        compose_file = live.compose_file or None
    elif live.provider:
        repository = _join_repository(live)
        if repository:
            source = GitSource(provider=live.provider, repository=repository, branch=live.branch or "main")
            compose_path = live.compose_path
    return ComposeService(
        name=live.name,
        description=live.description or None,
        source=source,
        compose_file=compose_file,
        compose_path=compose_path,
        command=live.command or None,
        env=_redact_env(live, include_secrets, warnings),
    )


def _export_application(live: LiveService, include_secrets: bool, warnings: list[str]) -> ApplicationService:
    source = None
    image = None
    if live.source_type == "docker":
        image = live.docker_image
    elif live.provider:
        repository = _join_repository(live)
        if repository:
            source = GitSource(provider=live.provider, repository=repository, branch=live.branch or "main")
    return ApplicationService(
        name=live.name,
        description=live.description or None,
        source=source,
        image=image,
        build_type=live.build_type,
        dockerfile_location=live.dockerfile_location,
        build_path=live.build_path,
        env=_redact_env(live, include_secrets, warnings),
    )


def _export_database(live: LiveService, include_secrets: bool, warnings: list[str]) -> DatabaseService:
    if live.database_password:
        warnings.append(
            f"Database password of '{live.name}' was not exported. "
            "Set password or password_cmd in the manifest for apply."
        )
    return DatabaseService(
        type=live.type,  # type: ignore[arg-type]
        name=live.name,
        description=live.description or None,
        image=live.docker_image,
        database_name=live.database_name,
        database_user=live.database_user,
        password=None,
        password_cmd=None,
        env=_redact_env(live, include_secrets, warnings),
    )


def _join_repository(live: LiveService) -> str:
    if live.repository and live.owner:
        return f"{live.owner}/{live.repository}"
    return live.repository or ""
