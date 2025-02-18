"""Configuration model."""

import json
import subprocess
from typing import Any

from pydantic import BaseModel, Field, HttpUrl, SecretStr, field_serializer, model_validator
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict, YamlConfigSettingsSource


class ConnectionConfig(BaseModel):
    """Connection config."""

    name: str = Field(
        ...,
        min_length=3,
        max_length=100,
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
        description="A name for the connection.",
    )
    url: HttpUrl = Field(..., description="The URL of the dokploy instance.")
    api_key: SecretStr | None = Field(
        None,
        min_length=40,
        max_length=40,
        description="An API key for the dokploy instance.",
    )
    api_key_cmd: str | None = Field(None, description="A command to get the API key.")
    notes: str = Field(default="", description="Notes about the connection.")

    @field_serializer("api_key", when_used="json")
    def dump_secret(self, v):
        """Allows dumping secret values."""
        return v.get_secret_value()

    def model_dump_clear(self, **kwargs) -> dict[str, Any]:
        """Allows dumping the config with clear secrets."""
        return json.loads(self.model_dump_json(**kwargs))

    @model_validator(mode="after")
    def check_api_key_or_cmd(self) -> "ConnectionConfig":
        """Validate api_key or api_key_cmd is provided."""
        if not self.api_key and not self.api_key_cmd:
            raise ValueError("Must provide api_key or api_key_cmd.")
        return self

    def get_api_key(self) -> str:
        """Returns the API key for the connection."""
        if self.api_key is not None:
            return self.api_key.get_secret_value()
        assert self.api_key_cmd, "Must provide api_key or api_key_cmd."
        return subprocess.check_output(self.api_key_cmd.split()).decode("utf-8")


class Config(BaseSettings):
    """Dokli config."""

    connections: list[ConnectionConfig] = Field(default_factory=list)
    model_config = SettingsConfigDict(
        env_prefix="DOKLI_",
        yaml_file=[
            "dokli.yaml",
            "~/.config/dokli/dokli.yaml",
        ],
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """Override default settings sources."""
        return (
            env_settings,
            init_settings,
            dotenv_settings,
            file_secret_settings,
            YamlConfigSettingsSource(settings_cls),
        )

    def get_connection(self, name: str) -> ConnectionConfig:
        """Get connection config."""
        return next(filter(lambda x: x.name == name, self.connections))
