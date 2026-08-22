"""Configuration model."""

import json
import os
import subprocess
from pathlib import Path
from typing import Any, Literal

import yaml
from click import BadParameter
from click.shell_completion import CompletionItem
from pydantic import BaseModel, Field, HttpUrl, SecretStr, field_serializer, model_validator
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict, YamlConfigSettingsSource

from dokli.secrets import conn_account, get_secret


def complete_connection_names(ctx: Any, param: Any, incomplete: str) -> list[CompletionItem]:
    """Click shell completion for the configured connection names."""
    names = [connection.name for connection in Config().connections]
    return [CompletionItem(name) for name in names if name.startswith(incomplete)]


def resolve_connection(config: "Config", name: str | None) -> "ConnectionConfig":
    """Resolve a connection by name, the default, or the only configured one.

    Priority: an explicit ``name`` wins; otherwise the configured
    ``default_connection`` (set via ``dokli use``); otherwise the single
    configured connection.
    """
    if name is not None:
        for connection in config.connections:
            if connection.name == name:
                return connection
        raise BadParameter(f"Unknown connection '{name}'.")
    if config.default_connection is not None:
        for connection in config.connections:
            if connection.name == config.default_connection:
                return connection
    if len(config.connections) == 1:
        return config.connections[0]
    raise BadParameter("Specify a connection name.")


# Textual ColorSystem fields users may override.
TUI_COLOR_FIELDS = frozenset(
    {"primary", "secondary", "warning", "error", "success", "accent", "background", "surface", "panel", "boost"}
)


class TuiKeysConfig(BaseModel):
    """TUI keybinding remaps (issue #61)."""

    app: dict[str, str] = Field(
        default_factory=dict,
        description=(
            "App-level action -> key (toggle_dark, connections, help, quit, " "command_palette, pick_action, cancel)."
        ),
    )
    verbs: dict[str, str] = Field(
        default_factory=dict,
        description=(
            "Action verb -> key. Extends or overrides the curated VERB_KEYS "
            "(create, update, save, start, stop, remove, deploy, restart, "
            "readLogs, rebuild, move, duplicate, rollback, ...); verbs without "
            "a key are reachable only through the palette (ctrl+p) or the "
            "action picker (ctrl+shift+p)."
        ),
    )


class TuiConfig(BaseModel):
    """TUI display & behavior options (issue #61)."""

    theme: Literal["dark", "light"] = Field("dark", description="Initial theme variant.")
    colors: dict[str, str] = Field(
        default_factory=dict,
        description=(
            "ColorSystem field overrides, applied to both theme variants. "
            f"Valid fields: {', '.join(sorted(TUI_COLOR_FIELDS))}."
        ),
    )
    keys: TuiKeysConfig = Field(default_factory=TuiKeysConfig)
    entity_colors: dict[str, str] = Field(
        default_factory=dict,
        description="Per-entity icon color overrides (e.g. compose: '#a6e3a1').",
    )
    state_colors: dict[str, str] = Field(
        default_factory=dict,
        description="Per-container-state color overrides (running, exited, dead, ...).",
    )
    entity_order: list[str] = Field(
        default_factory=list,
        description="Entities surfaced first in the browser list (empty = default 'project' first).",
    )
    auto_deploy: bool = Field(False, description="Deploy a service after a create/update from a form (best effort).")
    logs_interval_seconds: float = Field(
        3.0, description="How often the logs follow-mode polls for new lines (issue #72)."
    )
    logs_tail_lines: int = Field(500, description="How many lines each logs follow-mode poll requests (issue #72).")

    @property
    def dark(self) -> bool:
        """Whether the app should start in dark mode."""
        return self.theme == "dark"


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
    tui: TuiConfig = Field(default_factory=TuiConfig, description="TUI display & behavior options.")
    default_connection: str | None = Field(
        None, description="Default connection name used when none is passed (set via `dokli use`)."
    )
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
        data: dict[str, Any] = {"connections": connections}
        if self.default_connection is not None:
            data["default_connection"] = self.default_connection
        target.write_text(yaml.safe_dump(data, sort_keys=False))
