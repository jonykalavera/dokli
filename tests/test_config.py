"""Config tests."""

import yaml
import pytest
import typer
from polyfactory.factories.pydantic_factory import ModelFactory
from pydantic import ValidationError
from pydantic_settings import SettingsConfigDict

from dokli.config import Config, ConnectionConfig, TuiConfig


class ConnectionConfigFactory(ModelFactory[ConnectionConfig]):
    """Connection factory."""

    api_key = None
    api_key_cmd = "echo 'my api key from cmd'"


class ConfigFactory(ModelFactory[Config]):
    """Config factory."""

    connections = [ConnectionConfigFactory.build()]


class TestConfig:
    """Config model tests."""

    def test_config(self):
        """We expect to be able to declare an api with connections."""
        config = ConfigFactory.build()
        assert config.connections

    def test_get_connection(self):
        """We expect to be able to get a connection by name."""
        connection = ConnectionConfigFactory.build(name="dokploy")
        config = ConfigFactory.build(connections=[connection])
        assert config.get_connection("dokploy")

    def test_save_round_trip(self, tmp_path):
        """We expect save() to persist connections and reload them."""
        target = tmp_path / "dokli.yaml"
        config = ConfigFactory.build(
            connections=[
                ConnectionConfigFactory.build(name="alpha", api_key_cmd="echo key"),
                ConnectionConfigFactory.build(name="stage", api_key="*" * 64),
            ]
        )
        config.save(target)

        data = yaml.safe_load(target.read_text())
        assert [c["name"] for c in data["connections"]] == ["alpha", "stage"]
        assert data["connections"][0]["api_key_cmd"] == "echo key"
        assert data["connections"][1]["api_key"] == "*" * 64

        reloaded = [ConnectionConfig.model_validate(c) for c in data["connections"]]
        assert [c.name for c in reloaded] == ["alpha", "stage"]
        assert reloaded[1].api_key.get_secret_value() == "*" * 64

    def test_config_path_prefers_local(self, tmp_path, monkeypatch):
        """We expect a local dokli.yaml in the cwd to be the save target."""
        (tmp_path / "dokli.yaml").write_text("connections: []\n")
        monkeypatch.chdir(tmp_path)
        config = ConfigFactory.build()
        assert config._config_path().resolve() == (tmp_path / "dokli.yaml").resolve()

    def test_save_uses_local_file(self, tmp_path, monkeypatch):
        """We expect save() without a path to write to the local dokli.yaml."""
        (tmp_path / "dokli.yaml").write_text("connections: []\n")
        monkeypatch.chdir(tmp_path)
        config = ConfigFactory.build(connections=[ConnectionConfigFactory.build(name="alpha")])
        config.save()
        data = yaml.safe_load((tmp_path / "dokli.yaml").read_text())
        assert data["connections"][0]["name"] == "alpha"

    def test_save_persists_default_connection(self, tmp_path):
        """We expect save() to persist default_connection and reload it."""
        target = tmp_path / "dokli.yaml"
        config = ConfigFactory.build(
            connections=[ConnectionConfigFactory.build(name="alpha")],
            default_connection="alpha",
        )
        config.save(target)
        data = yaml.safe_load(target.read_text())
        assert data["default_connection"] == "alpha"

    def test_save_omits_default_connection_when_unset(self, tmp_path):
        """We expect no default_connection key when it is not set."""
        target = tmp_path / "dokli.yaml"
        config = ConfigFactory.build(connections=[ConnectionConfigFactory.build(name="alpha")], default_connection=None)
        config.save(target)
        data = yaml.safe_load(target.read_text())
        assert "default_connection" not in data


class TestResolveConnection:
    """Connection resolution with a configured default."""

    def test_default_connection_wins_over_nothing(self):
        """We expect the configured default to be used when no name is passed."""
        from dokli.config import resolve_connection

        config = ConfigFactory.build(
            connections=[
                ConnectionConfigFactory.build(name="alpha"),
                ConnectionConfigFactory.build(name="beta"),
            ],
            default_connection="beta",
        )
        assert resolve_connection(config, None).name == "beta"

    def test_explicit_name_beats_default(self):
        """We expect an explicit name to override the default."""
        from dokli.config import resolve_connection

        config = ConfigFactory.build(
            connections=[
                ConnectionConfigFactory.build(name="alpha"),
                ConnectionConfigFactory.build(name="beta"),
            ],
            default_connection="beta",
        )
        assert resolve_connection(config, "alpha").name == "alpha"

    def test_missing_default_falls_back_to_single(self):
        """We expect a missing default to fall back to the single connection."""
        from dokli.config import resolve_connection

        config = ConfigFactory.build(connections=[ConnectionConfigFactory.build(name="alpha")])
        assert resolve_connection(config, None).name == "alpha"


class TestUseCommand:
    """`dokli use` sets the default connection."""

    def test_use_sets_default(self, mocker):
        """We expect `dokli use <name>` to set and persist the default."""
        from dokli.connections import set_default_connection

        config = ConfigFactory.build(
            connections=[
                ConnectionConfigFactory.build(name="alpha"),
                ConnectionConfigFactory.build(name="beta"),
            ]
        )
        save = mocker.patch.object(Config, "save")

        set_default_connection(config, "beta")
        assert config.default_connection == "beta"
        assert save.called

    def test_use_unknown_connection_fails(self, mocker):
        """We expect `dokli use <unknown>` to error."""
        from dokli.connections import set_default_connection

        config = ConfigFactory.build(connections=[ConnectionConfigFactory.build(name="alpha")])
        with pytest.raises(typer.BadParameter):
            set_default_connection(config, "nope")

    def test_use_unset_clears_default(self, mocker):
        """We expect `dokli use --unset` to clear and persist the default."""
        from dokli.connections import unset_default_connection

        config = ConfigFactory.build(
            connections=[ConnectionConfigFactory.build(name="alpha")],
            default_connection="alpha",
        )
        save = mocker.patch.object(Config, "save")
        unset_default_connection(config)
        assert config.default_connection is None
        assert save.called


class TestConnectionConfig:
    """Connection config model tests."""

    def test_must_provide_api_key_or_cmd(self):
        """We expect to raise an error if no api key or cmd is provided."""
        with pytest.raises(ValidationError):
            ConnectionConfig(name="dokli", url="https://dokli.example.com")

    def test_connection_with_api_key(self):
        """We expect to be able to declare a connection with an API key."""
        config = ConnectionConfigFactory.build(api_key="*" * 64)
        assert config.get_api_key() == config.api_key.get_secret_value()

    def test_connection_with_api_key_cmd(self, mocker):
        """We expect to be able to declare a connection with an API key command."""
        config = ConnectionConfigFactory.build()
        assert config.api_key is None
        check_output = mocker.patch("dokli.config.subprocess.check_output", return_value=b"my api key from cmd")
        assert config.get_api_key() == "my api key from cmd"
        check_output.assert_called_once_with(config.api_key_cmd, shell=True)

    def test_get_api_key_prefers_keyring(self, fake_keyring):
        """We expect the keychain to be used before api_key_cmd."""
        fake_keyring.store[("dokli", "conn.alpha")] = "*" * 64
        config = ConnectionConfigFactory.build(
            name="alpha", api_key=None, api_key_keyring=True, api_key_cmd="echo key"
        )
        assert config.get_api_key() == "*" * 64

    def test_api_key_cmd_supports_pipes(self, mocker):
        """We expect the API key command to run through a shell (pipes work)."""
        config = ConnectionConfigFactory.build(api_key_cmd="printf secret | tr a-z A-Z")
        mocker.patch("dokli.config.subprocess.check_output", return_value=b"SECRET")
        assert config.get_api_key() == "SECRET"

    def test_model_dump_clear_prints_clear_secrets(self):
        """We expect to be able to dump the config with clear secrets."""
        config = ConnectionConfigFactory.build(api_key="*" * 64)
        result = config.model_dump_clear()
        assert result["api_key"] == "*" * 64


class TestTuiConfig:
    """TUI customization options (issue #61)."""

    def test_defaults(self):
        """We expect sane defaults (dark theme, no overrides)."""
        tui = TuiConfig()
        assert tui.dark is True
        assert tui.colors == {}
        assert tui.keys.app == {}
        assert tui.keys.verbs == {}
        assert tui.auto_deploy is False

    def test_parses_from_yaml(self, tmp_path):
        """We expect the tui section to load from the config file."""
        target = tmp_path / "dokli.yaml"
        target.write_text(
            """\
connections:
  - name: alpha
    url: https://alpha.lan
    api_key_cmd: "echo key"
tui:
  theme: light
  colors:
    primary: "#111111"
  entity_colors:
    compose: "#a6e3a1"
  state_colors:
    running: "#f9e2af"
  entity_order:
    - project
    - server
  keys:
    app:
      connections: "n"
    verbs:
      deploy: "z"
  auto_deploy: true
"""
        )

        class IsolatedConfig(Config):
            model_config = SettingsConfigDict(env_prefix="DOKLI_", yaml_file=[str(target)])

        config = IsolatedConfig()
        assert config.tui.dark is False
        assert config.tui.colors == {"primary": "#111111"}
        assert config.tui.entity_colors == {"compose": "#a6e3a1"}
        assert config.tui.state_colors == {"running": "#f9e2af"}
        assert config.tui.entity_order == ["project", "server"]
        assert config.tui.keys.app == {"connections": "n"}
        assert config.tui.keys.verbs == {"deploy": "z"}
        assert config.tui.auto_deploy is True

    def test_unknown_colors_are_ignored(self):
        """We expect unknown color fields to be ignored (no crash)."""
        tui = TuiConfig(colors={"not_a_field": "#fff"})
        assert tui.colors == {"not_a_field": "#fff"}
