"""Configuration model."""

import json
from typing import Any

from pydantic import BaseModel, Field, HttpUrl, SecretStr, field_serializer
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
    api_key: SecretStr = Field(
        ...,
        min_length=40,
        max_length=40,
        description="The API key for the dokploy instance.",
    )
    notes: str = Field(default="", description="Notes about the connection.")

    @field_serializer("api_key", when_used="json")
    def dump_secret(self, v):
        """Allows dumping secret values."""
        return v.get_secret_value()

    def model_dump_clear(self, **kwargs) -> dict[str, Any]:
        """Allows dumping the config with clear secrets."""
        return json.loads(self.model_dump_json(**kwargs))


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
