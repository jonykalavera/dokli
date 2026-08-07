"""Configuration model."""

import json
import os
import subprocess
from pathlib import Path
from typing import Any

import yaml
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
        min_length=64,
        max_length=64,
        description="An API key for the dokploy instance.",
    )
    api_key_cmd: str | None = Field(None, description="A command to get the API key.")
    api_key_keyring: bool = Field(
        False, description="Store the API key in the system keychain instead of the config file."
    )
    notes: str = Field(default="", description="Notes about the connection.")

    @field_serializer("api_key", when_used="json")
    def dump_secret(self, v):
        """Allows dumping secret values."""
        return v.get_secret_value() if v is not None else None

    def model_dump_clear(self, **kwargs) -> dict[str, Any]:
        """Allows dumping the config with clear secrets."""
        return json.loads(self.model_dump_json(**kwargs))

    @model_validator(mode="after")
    def check_api_key_or_cmd(self) -> "ConnectionConfig":
        """Validate api_key, api_key_keyring or api_key_cmd is provided."""
        if not self.api_key and not self.api_key_keyring and not self.api_key_cmd:
            raise ValueError("Must provide api_key, api_key_keyring or api_key_cmd.")
        return self

    def get_api_key(self) -> str:
        """Returns the API key for the connection.

        Resolution order: literal ``api_key``, then the system keychain
        (``api_key_keyring``), then ``api_key_cmd``.
        """
        if self.api_key is not None:
            return self.api_key.get_secret_value()
        if self.api_key_keyring:
            from dokli.secrets import conn_account, get_secret

            value = get_secret(conn_account(self.name))
            if value:
                return value
        assert self.api_key_cmd, "Must provide api_key, api_key_keyring or api_key_cmd."
        raw_output = subprocess.check_output(self.api_key_cmd, shell=True)
        output = raw_output.decode("utf-8").strip().strip("\n")
        return output


class Config(BaseSettings):
    """Dokli config."""

    connections: list[ConnectionConfig] = Field(default_factory=list)
    model_config = SettingsConfigDict(
        env_prefix="DOKLI_",
        yaml_file=[
            "dokli.yaml",
            os.getenv("DOKLI_CONFIG", "~/.config/dokli/dokli.yaml"),
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

    def _config_path(self) -> Path:
        """The config file to save to, mirroring the load order.

        ``dokli.yaml`` in the cwd wins over ``DOKLI_CONFIG``/the default, just
        like ``yaml_file`` loading.
        """
        candidates = [
            "dokli.yaml",
            os.getenv("DOKLI_CONFIG", "~/.config/dokli/dokli.yaml"),
        ]
        for candidate in candidates:
            path = Path(candidate).expanduser()
            if path.exists():
                return path
        return Path(candidates[-1]).expanduser()

    def save(self, path: str | Path | None = None) -> None:
        """Persist connections to the YAML config file.

        Args:
            path: Where to write. Defaults to the config file that would be
                loaded (``dokli.yaml`` if present, else ``DOKLI_CONFIG`` or
                ``~/.config/dokli/dokli.yaml``).
        """
        target = Path(path).expanduser() if path is not None else self._config_path()
        target.parent.mkdir(parents=True, exist_ok=True)
        connections = [
            {key: value for key, value in connection.model_dump(mode="json").items() if value is not None}
            for connection in self.connections
        ]
        target.write_text(yaml.safe_dump({"connections": connections}, sort_keys=False))
