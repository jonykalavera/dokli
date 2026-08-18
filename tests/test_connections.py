"""Connection management CLI tests (issue #47)."""

import typer
import yaml
from typer.testing import CliRunner

from dokli.config import Config, ConnectionConfig
from dokli.connections import build_command

runner = CliRunner()


def _config(tmp_path, monkeypatch, connections=None):
    (tmp_path / "dokli.yaml").write_text("connections: []\n")
    monkeypatch.chdir(tmp_path)
    return Config(connections=connections or [])


def _app(config):
    app = typer.Typer()
    app.add_typer(build_command(config))
    return app


def _conn(name="alpha", url="https://a.example.com"):
    return ConnectionConfig(name=name, url=url, api_key="*" * 64)


def test_add_connection_persists(tmp_path, monkeypatch):
    """We expect add to save the connection to the config file."""
    config = _config(tmp_path, monkeypatch)
    result = runner.invoke(
        _app(config),
        [
            "connections",
            "add",
            "stage",
            "--url",
            "https://stage.example.com",
            "--api-key",
            "*" * 64,
            "--notes",
            "staging",
        ],
    )
    assert result.exit_code == 0
    assert config.connections[0].name == "stage"
    saved = yaml.safe_load((tmp_path / "dokli.yaml").read_text())
    assert saved["connections"][0]["name"] == "stage"


def test_add_connection_with_keyring(tmp_path, monkeypatch, fake_keyring):
    """We expect --keyring to store the key in the keychain, not the config."""
    config = _config(tmp_path, monkeypatch)
    result = runner.invoke(
        _app(config),
        ["connections", "add", "stage", "--url", "https://stage.example.com", "--api-key", "*" * 64, "--keyring"],
    )
    assert result.exit_code == 0
    connection = config.connections[0]
    assert connection.api_key is None
    assert connection.api_key_keyring is True
    assert fake_keyring.store[("dokli", "conn.stage")] == "*" * 64
    assert "*" * 64 not in (tmp_path / "dokli.yaml").read_text()


def test_update_connection_with_keyring(tmp_path, monkeypatch, fake_keyring):
    """We expect --keyring on update to move the key to the keychain."""
    config = _config(tmp_path, monkeypatch, connections=[_conn()])
    result = runner.invoke(_app(config), ["connections", "update", "alpha", "--keyring"])
    assert result.exit_code == 0
    updated = config.connections[0]
    assert updated.api_key is None
    assert updated.api_key_keyring is True
    assert fake_keyring.store[("dokli", "conn.alpha")] == "*" * 64


def test_add_prompts_for_missing_name_and_url(tmp_path, monkeypatch):
    """We expect add to prompt for name and url when not provided."""
    config = _config(tmp_path, monkeypatch)
    result = runner.invoke(
        _app(config),
        ["connections", "add", "--api-key", "*" * 64],
        input="newconn\nhttps://new.example.com\n",
    )
    assert result.exit_code == 0
    assert config.connections[0].name == "newconn"
    assert config.connections[0].url.host == "new.example.com"


def test_add_duplicate_rejected(tmp_path, monkeypatch):
    """We expect adding an existing connection to fail."""
    config = _config(tmp_path, monkeypatch, connections=[_conn()])
    result = runner.invoke(
        _app(config), ["connections", "add", "alpha", "--url", "https://b.example.com", "--api-key", "*" * 64]
    )
    assert result.exit_code == 2
    assert "already exists" in result.output


def test_add_invalid_name_rejected(tmp_path, monkeypatch):
    """We expect an invalid connection name to fail validation."""
    config = _config(tmp_path, monkeypatch)
    result = runner.invoke(
        _app(config), ["connections", "add", "BAD NAME", "--url", "https://a.example.com", "--api-key", "*" * 64]
    )
    assert result.exit_code == 2


def test_update_no_fields_warns(tmp_path, monkeypatch):
    """We expect update without any field to warn instead of claiming success."""
    config = _config(tmp_path, monkeypatch, connections=[_conn()])
    result = runner.invoke(_app(config), ["connections", "update", "alpha"])
    assert result.exit_code == 0
    assert "No fields provided" in result.output
    assert "Updated" not in result.output


def test_update_connection(tmp_path, monkeypatch):
    """We expect update to change only the given fields."""
    config = _config(tmp_path, monkeypatch, connections=[_conn()])
    result = runner.invoke(
        _app(config), ["connections", "update", "alpha", "--url", "https://b.example.com", "--notes", "prod"]
    )
    assert result.exit_code == 0
    assert config.connections[0].url.host == "b.example.com"
    assert config.connections[0].notes == "prod"


def test_update_api_key_cmd_replaces_key(tmp_path, monkeypatch):
    """We expect setting an api-key-cmd to drop the stored api key."""
    config = _config(tmp_path, monkeypatch, connections=[_conn()])
    result = runner.invoke(
        _app(config), ["connections", "update", "alpha", "--api-key-cmd", "secret-tool lookup dokli alpha"]
    )
    assert result.exit_code == 0
    updated = config.connections[0]
    assert updated.api_key is None
    assert updated.api_key_cmd == "secret-tool lookup dokli alpha"


def test_remove_connection(tmp_path, monkeypatch):
    """We expect remove to delete the connection from the config."""
    config = _config(tmp_path, monkeypatch, connections=[_conn()])
    result = runner.invoke(_app(config), ["connections", "remove", "alpha"])
    assert result.exit_code == 0
    assert config.connections == []


def test_rename_connection(tmp_path, monkeypatch):
    """We expect update with a second positional to rename the connection."""
    config = _config(tmp_path, monkeypatch, connections=[_conn()])
    result = runner.invoke(_app(config), ["connections", "update", "alpha", "gamma"])
    assert result.exit_code == 0
    assert [c.name for c in config.connections] == ["gamma"]
    assert "alpha" not in [c.name for c in config.connections]


def test_rename_duplicate_rejected(tmp_path, monkeypatch):
    """We expect renaming to an existing connection name to fail."""
    config = _config(tmp_path, monkeypatch, connections=[_conn(), _conn(name="beta", url="https://b.example.com")])
    result = runner.invoke(_app(config), ["connections", "update", "alpha", "beta"])
    assert result.exit_code == 2
    assert "already exists" in result.output


def test_rename_invalid_name_rejected(tmp_path, monkeypatch):
    """We expect renaming to an invalid name to fail validation."""
    config = _config(tmp_path, monkeypatch, connections=[_conn()])
    result = runner.invoke(_app(config), ["connections", "update", "alpha", "BAD NAME"])
    assert result.exit_code == 2


def test_rename_same_name_noop(tmp_path, monkeypatch):
    """We expect renaming to the same name with no fields to warn and change nothing."""
    config = _config(tmp_path, monkeypatch, connections=[_conn()])
    result = runner.invoke(_app(config), ["connections", "update", "alpha", "alpha"])
    assert result.exit_code == 0
    assert "No fields provided" in result.output
    assert [c.name for c in config.connections] == ["alpha"]


def test_rename_same_name_applies_fields(tmp_path, monkeypatch):
    """We expect same-name rename to still apply the other field updates."""
    config = _config(tmp_path, monkeypatch, connections=[_conn()])
    result = runner.invoke(_app(config), ["connections", "update", "alpha", "alpha", "--notes", "prod"])
    assert result.exit_code == 0
    assert "rename skipped" in result.output
    updated = config.connections[0]
    assert updated.name == "alpha"
    assert updated.notes == "prod"


def test_rename_with_fields(tmp_path, monkeypatch):
    """We expect rename to combine with other field updates."""
    config = _config(tmp_path, monkeypatch, connections=[_conn()])
    result = runner.invoke(
        _app(config), ["connections", "update", "alpha", "gamma", "--notes", "prod"]
    )
    assert result.exit_code == 0
    updated = config.connections[0]
    assert updated.name == "gamma"
    assert updated.notes == "prod"


def test_get_masks_key(tmp_path, monkeypatch):
    """We expect get to show the connection with the key masked."""
    config = _config(tmp_path, monkeypatch, connections=[_conn()])
    result = runner.invoke(_app(config), ["connections", "get", "alpha"])
    assert result.exit_code == 0
    assert "***" in result.output
    assert "*" * 64 not in result.output


def test_ls_lists_connections(tmp_path, monkeypatch):
    """We expect ls to list the configured connections."""
    connection = ConnectionConfig(
        name="alpha", url="https://a.example.com", api_key_cmd="secret-tool lookup dokli alpha", notes="prod"
    )
    config = _config(tmp_path, monkeypatch, connections=[connection])
    result = runner.invoke(_app(config), ["connections", "ls"])
    assert result.exit_code == 0
    assert "alpha" in result.output
    assert "prod" in result.output


def test_test_connection_ok(tmp_path, monkeypatch, mocker):
    """We expect test to hit the live instance (force_refresh) and report the version."""
    config = _config(tmp_path, monkeypatch, connections=[_conn()])
    client = mocker.Mock()
    client.schema = {"info": {"version": "v0.29.13"}}
    api_client = mocker.patch("dokli.connections.APIClient", return_value=client)
    result = runner.invoke(_app(config), ["connections", "test", "alpha"])
    assert result.exit_code == 0
    assert "v0.29.13" in result.output
    api_client.assert_called_once_with(config.connections[0], force_refresh=True)


def test_test_connection_unreachable(tmp_path, monkeypatch, mocker):
    """We expect test to fail with a non-zero exit when unreachable."""
    config = _config(tmp_path, monkeypatch, connections=[_conn()])
    mocker.patch("dokli.connections.APIClient", side_effect=RuntimeError("boom"))
    result = runner.invoke(_app(config), ["connections", "test", "alpha"])
    assert result.exit_code == 1
    assert "unreachable" in result.output
