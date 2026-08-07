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


def _conn(name="meche", url="https://a.example.com"):
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
        _app(config), ["connections", "add", "meche", "--url", "https://b.example.com", "--api-key", "*" * 64]
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
    result = runner.invoke(_app(config), ["connections", "update", "meche"])
    assert result.exit_code == 0
    assert "No fields provided" in result.output
    assert "Updated" not in result.output


def test_update_connection(tmp_path, monkeypatch):
    """We expect update to change only the given fields."""
    config = _config(tmp_path, monkeypatch, connections=[_conn()])
    result = runner.invoke(
        _app(config), ["connections", "update", "meche", "--url", "https://b.example.com", "--notes", "prod"]
    )
    assert result.exit_code == 0
    assert config.connections[0].url.host == "b.example.com"
    assert config.connections[0].notes == "prod"


def test_update_api_key_cmd_replaces_key(tmp_path, monkeypatch):
    """We expect setting an api-key-cmd to drop the stored api key."""
    config = _config(tmp_path, monkeypatch, connections=[_conn()])
    result = runner.invoke(
        _app(config), ["connections", "update", "meche", "--api-key-cmd", "secret-tool lookup dokli meche"]
    )
    assert result.exit_code == 0
    updated = config.connections[0]
    assert updated.api_key is None
    assert updated.api_key_cmd == "secret-tool lookup dokli meche"


def test_remove_connection(tmp_path, monkeypatch):
    """We expect remove to delete the connection from the config."""
    config = _config(tmp_path, monkeypatch, connections=[_conn()])
    result = runner.invoke(_app(config), ["connections", "remove", "meche"])
    assert result.exit_code == 0
    assert config.connections == []


def test_rename_connection(tmp_path, monkeypatch):
    """We expect update with a second positional to rename the connection."""
    config = _config(tmp_path, monkeypatch, connections=[_conn()])
    result = runner.invoke(_app(config), ["connections", "update", "meche", "media-main"])
    assert result.exit_code == 0
    assert [c.name for c in config.connections] == ["media-main"]
    assert "meche" not in [c.name for c in config.connections]


def test_rename_duplicate_rejected(tmp_path, monkeypatch):
    """We expect renaming to an existing connection name to fail."""
    config = _config(tmp_path, monkeypatch, connections=[_conn(), _conn(name="hot-test", url="https://b.example.com")])
    result = runner.invoke(_app(config), ["connections", "update", "meche", "hot-test"])
    assert result.exit_code == 2
    assert "already exists" in result.output


def test_rename_invalid_name_rejected(tmp_path, monkeypatch):
    """We expect renaming to an invalid name to fail validation."""
    config = _config(tmp_path, monkeypatch, connections=[_conn()])
    result = runner.invoke(_app(config), ["connections", "update", "meche", "BAD NAME"])
    assert result.exit_code == 2


def test_rename_same_name_warns(tmp_path, monkeypatch):
    """We expect renaming to the same name to warn and not change anything."""
    config = _config(tmp_path, monkeypatch, connections=[_conn()])
    result = runner.invoke(_app(config), ["connections", "update", "meche", "meche"])
    assert result.exit_code == 0
    assert "already named" in result.output
    assert [c.name for c in config.connections] == ["meche"]


def test_rename_with_fields(tmp_path, monkeypatch):
    """We expect rename to combine with other field updates."""
    config = _config(tmp_path, monkeypatch, connections=[_conn()])
    result = runner.invoke(
        _app(config), ["connections", "update", "meche", "media-main", "--notes", "prod"]
    )
    assert result.exit_code == 0
    updated = config.connections[0]
    assert updated.name == "media-main"
    assert updated.notes == "prod"


def test_get_masks_key(tmp_path, monkeypatch):
    """We expect get to show the connection with the key masked."""
    config = _config(tmp_path, monkeypatch, connections=[_conn()])
    result = runner.invoke(_app(config), ["connections", "get", "meche"])
    assert result.exit_code == 0
    assert "***" in result.output
    assert "*" * 64 not in result.output


def test_ls_lists_connections(tmp_path, monkeypatch):
    """We expect ls to list the configured connections."""
    connection = ConnectionConfig(
        name="meche", url="https://a.example.com", api_key_cmd="secret-tool lookup dokli meche", notes="prod"
    )
    config = _config(tmp_path, monkeypatch, connections=[connection])
    result = runner.invoke(_app(config), ["connections", "ls"])
    assert result.exit_code == 0
    assert "meche" in result.output
    assert "prod" in result.output


def test_test_connection_ok(tmp_path, monkeypatch, mocker):
    """We expect test to report the Dokploy version on success."""
    config = _config(tmp_path, monkeypatch, connections=[_conn()])
    client = mocker.Mock()
    client.schema = {"info": {"version": "v0.29.13"}}
    mocker.patch("dokli.connections.APIClient", return_value=client)
    result = runner.invoke(_app(config), ["connections", "test", "meche"])
    assert result.exit_code == 0
    assert "v0.29.13" in result.output


def test_test_connection_unreachable(tmp_path, monkeypatch, mocker):
    """We expect test to fail with a non-zero exit when unreachable."""
    config = _config(tmp_path, monkeypatch, connections=[_conn()])
    mocker.patch("dokli.connections.APIClient", side_effect=RuntimeError("boom"))
    result = runner.invoke(_app(config), ["connections", "test", "meche"])
    assert result.exit_code == 1
    assert "unreachable" in result.output
