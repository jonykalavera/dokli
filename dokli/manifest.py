"""Declarative manifest models for Dokli as Code.

The manifest (``dokploy.yaml``) describes the desired state of a Dokploy
instance. See :issue:`20` and :issue:`50`.
"""

from pathlib import Path
from typing import Annotated, Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field


class GitProvider(BaseModel):
    """A git provider referenced by services.

    Credentials are write-only in Dokploy's API, so they are never stored in
    the manifest. Use ``token_cmd`` to resolve them externally at apply time,
    mirroring ``ConnectionConfig.api_key_cmd``.
    """

    name: str
    provider: Literal["github", "gitlab", "gitea", "bitbucket"]
    url: str = Field(
        default="https://github.com",
        description="Provider URL. Needed for self-hosted gitea/gitlab or GitHub Enterprise.",
    )
    app_name: str | None = Field(default=None, description="GitHub App name (metadata only).")
    owner: str | None = Field(default=None, description="Provider owner/account (metadata only).")
    token_cmd: str | None = Field(
        default=None,
        description="Command that outputs the credential. Never store the value here.",
    )
    token_keyring: bool = Field(
        default=False,
        description="Store the credential in the system keychain (provider.<name>).",
    )


class GitSource(BaseModel):
    """A repository source backed by a git provider."""

    provider: str = Field(..., description="Name of the git_providers entry.")
    repository: str = Field(..., description="Repository path, e.g. owner/repo.")
    branch: str = Field(default="main")


class ComposeService(BaseModel):
    """A compose service."""

    type: Literal["compose"] = "compose"
    name: str
    description: str | None = None
    source: GitSource | None = Field(
        default=None,
        description="Git repository source. Mutually exclusive with compose_file.",
    )
    compose_file: str | None = Field(
        default=None,
        description="Raw compose YAML or a path to a local file. Mutually exclusive with source.",
    )
    compose_path: str | None = Field(
        default=None,
        description="Path to the compose file inside the repository.",
    )
    command: str | None = None
    env: str | None = Field(default=None, description="Environment variables as KEY=VALUE lines.")


class ApplicationService(BaseModel):
    """An application service."""

    type: Literal["application"] = "application"
    name: str
    description: str | None = None
    source: GitSource | None = Field(default=None, description="Git repository source.")
    image: str | None = Field(default=None, description="Docker image for a docker source.")
    build_type: str | None = Field(
        default=None,
        description="dockerfile, nixpacks, static, ...",
    )
    dockerfile_location: str | None = None
    build_path: str | None = None
    env: str | None = Field(default=None, description="Environment variables as KEY=VALUE lines.")


class DatabaseService(BaseModel):
    """A database service."""

    type: Literal["postgres", "mysql", "mariadb", "mongo", "redis"]
    name: str
    description: str | None = None
    image: str | None = None
    database_name: str | None = Field(default=None, description="Defaults to the service name.")
    database_user: str | None = Field(default=None, description="Defaults to the service name.")
    password: str | None = Field(
        default=None,
        description="Database password (secret). Prefer password_cmd; never commit real passwords.",
    )
    password_cmd: str | None = Field(
        default=None,
        description="Command that outputs the database password. Resolved at apply time.",
    )
    password_keyring: bool = Field(
        default=False,
        description="Store the database password in the system keychain (db.<name>).",
    )
    env: str | None = Field(default=None, description="Environment variables as KEY=VALUE lines.")


Service = Annotated[
    ComposeService | ApplicationService | DatabaseService,
    Field(discriminator="type"),
]


class EnvironmentDef(BaseModel):
    """A named environment with its services."""

    name: str
    services: list[Service] = Field(default_factory=list)


class ProjectDef(BaseModel):
    """A project with its services."""

    name: str
    description: str | None = None
    services: list[Service] = Field(
        default_factory=list,
        description="Services in the project's default environment.",
    )
    environments: list[EnvironmentDef] = Field(
        default_factory=list,
        description="Named environments (besides the default one).",
    )


class Resource(BaseModel):
    """A generic schema-driven resource (issue #50).

    ``kind`` is an entity from the OpenAPI registry, ``name`` is the match
    key, ``in`` is the explicit parent path (``<kind>:<name>[/<kind>:<name>]``)
    and ``data`` holds the create/update fields. Parent ids are derived from
    ``in``, never repeated in ``data``. Secret fields in ``data`` use dict
    references: ``{"cmd": ...}`` or ``{"keyring": ...}``.
    """

    model_config = ConfigDict(populate_by_name=True)

    kind: str
    name: str
    in_: str | None = Field(
        default=None,
        alias="in",
        description="Parent path, e.g. compose:torrents or project:media / environment:production.",
    )
    data: dict[str, Any] = Field(default_factory=dict, description="Create/update fields for the resource.")


class Manifest(BaseModel):
    """Dokli as Code manifest."""

    api_version: str = Field(default="v1", alias="apiVersion", description="Dokli manifest format version.")
    dokploy_version: str | None = Field(
        default=None,
        alias="dokployVersion",
        description="Dokploy API version the manifest was written against (stamped by init/export).",
    )
    connection: str = Field(..., description="Connection name from dokli's config.")
    server: str | None = Field(
        default=None,
        description="Server name to deploy to. Defaults to the local server.",
    )
    git_providers: list[GitProvider] = Field(default_factory=list)
    projects: list[ProjectDef] = Field(default_factory=list)
    resources: list[Resource] = Field(
        default_factory=list,
        description="Generic schema-driven resources (issue #50).",
    )

    def get_git_provider(self, name: str) -> GitProvider:
        """Get a git provider by name.

        Raises:
            ValueError: If the provider is not defined in the manifest.
        """
        try:
            return next(provider for provider in self.git_providers if provider.name == name)
        except StopIteration:
            raise ValueError(f"Git provider '{name}' is not defined in the manifest.") from None

    @classmethod
    def load(cls, path: str) -> "Manifest":
        """Load a manifest from a YAML file, validating the apiVersion."""
        with open(path) as file:
            data = yaml.safe_load(file) or {}
        api_version = data.get("apiVersion", "v1")
        if api_version != "v1":
            raise ValueError(f"Unsupported manifest apiVersion '{api_version}' (expected 'v1').")
        return cls.model_validate(data)


def load_manifests(path: str) -> list[Manifest]:
    """Load one manifest (file) or every ``*.yaml``/``*.yml`` in a directory."""
    target = Path(path)
    if not target.is_dir():
        return [Manifest.load(str(target))]
    files = sorted({*(target.glob("*.yaml")), *(target.glob("*.yml"))})
    return [Manifest.load(str(file)) for file in files]
