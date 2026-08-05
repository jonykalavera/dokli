"""Declarative manifest models for Dokli as Code.

The manifest (``dokli.yaml``) describes the desired state of a Dokploy
instance. See :issue:`20`.
"""

from typing import Annotated, Literal

import yaml
from pydantic import BaseModel, Field


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
    env: str | None = Field(default=None, description="Environment variables as KEY=VALUE lines.")


Service = Annotated[
    ComposeService | ApplicationService | DatabaseService,
    Field(discriminator="type"),
]


class ProjectDef(BaseModel):
    """A project with its services."""

    name: str
    description: str | None = None
    services: list[Service] = Field(default_factory=list)


class Manifest(BaseModel):
    """Dokli as Code manifest."""

    connection: str = Field(..., description="Connection name from dokli's config.")
    server: str | None = Field(
        default=None,
        description="Server name to deploy to. Defaults to the local server.",
    )
    git_providers: list[GitProvider] = Field(default_factory=list)
    projects: list[ProjectDef] = Field(default_factory=list)

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
        """Load a manifest from a YAML file."""
        with open(path) as file:
            return cls.model_validate(yaml.safe_load(file))
