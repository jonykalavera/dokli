"""Dokli CLI tests."""

import pytest
import typer

import dokli.cli
from dokli.cli import app, main, refresh_command, tui_command
from dokli.config import Config, ConnectionConfig, complete_connection_names
from dokli.openapi_cli import build_command


def test_loads_api_commands():
    """We expect the CLI to load API commands."""
    assert app.registered_groups[0].typer_instance.info.name == "api"


def test_loads_tui_command():
    """We expect the CLI to load TUI command."""
    assert "tui" in [cmd.name for cmd in app.registered_commands]


def test_loads_refresh_command():
    """We expect the CLI to load the refresh command."""
    assert "refresh" in [cmd.name for cmd in app.registered_commands]


def test_app_has_main_callback():
    """We expect the CLI to have a main callback."""
    assert app.registered_callback.callback is main
    assert app.registered_callback.no_args_is_help


def test_version_flag_prints_version():
    """We expect --version / -v to print the installed version and exit."""
    from typer.testing import CliRunner

    from dokli.cli import _cli_version

    for flag in ("--version", "-v"):
        result = CliRunner().invoke(app, [flag])
        assert result.exit_code == 0
        assert result.output.strip() == f"dokli {_cli_version()}"


_SCHEMA = {
    "openapi": "3.1.0",
    "info": {"title": "Dokploy API", "version": "v1.0"},
    "paths": {"/x.all": {"get": {}}},
    "components": {"schemas": {"x": {}}},
}


def _patch_schema(mocker):
    connection = ConnectionConfig(name="test-env", url="https://example.com", api_key_cmd="echo key")
    mocker.patch("dokli.cli._get_connection", return_value=connection)
    client = mocker.Mock()
    client.schema = _SCHEMA
    return mocker.patch("dokli.cli.APIClient", return_value=client)


def test_schema_command_dumps_json(mocker):
    """We expect schema to print the connection's OpenAPI document as JSON."""
    from typer.testing import CliRunner

    client = _patch_schema(mocker)
    result = CliRunner().invoke(app, ["schema", "test-env"])
    assert result.exit_code == 0
    assert '"title": "Dokploy API"' in result.output
    assert client.call_args.kwargs == {"force_refresh": False}


def test_schema_command_yaml(mocker):
    """We expect --format yaml to dump the schema as YAML."""
    from typer.testing import CliRunner

    _patch_schema(mocker)
    result = CliRunner().invoke(app, ["schema", "test-env", "--format", "yaml"])
    assert result.exit_code == 0
    assert "title: Dokploy API" in result.output


def test_schema_command_summary(mocker):
    """We expect --summary to print a compact overview."""
    from typer.testing import CliRunner

    _patch_schema(mocker)
    result = CliRunner().invoke(app, ["schema", "test-env", "--summary"])
    assert result.exit_code == 0
    assert "Connection: test-env" in result.output
    assert "Dokploy API version: v1.0" in result.output
    assert "Paths: 1" in result.output
    assert "Schemas: 1" in result.output


def test_schema_command_refresh(mocker):
    """We expect --refresh to force a schema refetch."""
    from typer.testing import CliRunner

    client = _patch_schema(mocker)
    result = CliRunner().invoke(app, ["schema", "test-env", "--refresh"])
    assert result.exit_code == 0
    assert client.call_args.kwargs == {"force_refresh": True}


class _FakeResponse:
    """Minimal response stand-in with a json() payload."""

    def __init__(self, data):
        self._data = data

    def json(self):
        return self._data


def _patch_logs_client(mocker):
    client = mocker.Mock()
    mocker.patch("dokli.logs_cli.APIClient", return_value=client)
    return client


def test_logs_one_shot_compose(mocker):
    """We expect compose logs without -f to hit compose.readLogs and exit."""
    from typer.testing import CliRunner

    connection = ConnectionConfig(name="test-env", url="https://example.com", api_key_cmd="echo key")
    mocker.patch("dokli.logs_cli.resolve_connection", return_value=connection)
    client = _patch_logs_client(mocker)
    client.request.return_value = _FakeResponse("line a\nline b\n")

    result = CliRunner().invoke(
        app, ["logs", "test-env", "--compose-id", "c1", "--container-id", "cc1", "-n", "2"]
    )
    assert result.exit_code == 0
    assert "line a" in result.output
    assert "line b" in result.output
    method, route, params = client.request.call_args[0]
    assert route == "compose.readLogs"
    assert params == {"composeId": "c1", "containerId": "cc1", "tail": 2}


def test_logs_one_shot_application(mocker):
    """We expect application logs without -f to hit application.readLogs."""
    from typer.testing import CliRunner

    connection = ConnectionConfig(name="test-env", url="https://example.com", api_key_cmd="echo key")
    mocker.patch("dokli.logs_cli.resolve_connection", return_value=connection)
    client = _patch_logs_client(mocker)
    client.request.return_value = _FakeResponse("app line\n")

    result = CliRunner().invoke(app, ["logs", "test-env", "--application-id", "a1", "-n", "2"])
    assert result.exit_code == 0
    assert "app line" in result.output
    method, route, params = client.request.call_args[0]
    assert route == "application.readLogs"
    assert params == {"applicationId": "a1", "tail": 2}


def test_logs_one_shot_deployment(mocker):
    """We expect deployment logs without -f to hit deployment.readLogs."""
    from typer.testing import CliRunner

    connection = ConnectionConfig(name="test-env", url="https://example.com", api_key_cmd="echo key")
    mocker.patch("dokli.logs_cli.resolve_connection", return_value=connection)
    client = _patch_logs_client(mocker)
    client.request.return_value = _FakeResponse("dep line\n")

    result = CliRunner().invoke(app, ["logs", "test-env", "--deployment-id", "d1", "-n", "2"])
    assert result.exit_code == 0
    assert "dep line" in result.output
    method, route, params = client.request.call_args[0]
    assert route == "deployment.readLogs"
    assert params == {"deploymentId": "d1", "tail": 2}


def test_logs_follow_compose_streams_ws(mocker):
    """We expect compose logs -f to stream the container WebSocket."""
    from typer.testing import CliRunner

    connection = ConnectionConfig(name="test-env", url="https://example.com", api_key_cmd="echo key")
    mocker.patch("dokli.logs_cli.resolve_connection", return_value=connection)

    async def fake_stream(connection, endpoint, params):
        assert endpoint == "/docker-container-logs"
        assert params == {"containerId": "cc1", "tail": 100}
        yield "2026-08-05T19:56:00Z live 1\r"
        yield "2026-08-05T19:56:01Z live 2\r"

    mocker.patch("dokli.logs_cli.iter_lines", side_effect=fake_stream)
    result = CliRunner().invoke(app, ["logs", "test-env", "--compose-id", "c1", "--container-id", "cc1", "-f"])
    assert result.exit_code == 0
    assert "live 1" in result.output
    assert "live 2" in result.output


def test_logs_follow_application_resolves_container(mocker):
    """We expect application logs -f to resolve the container then stream."""
    from typer.testing import CliRunner

    connection = ConnectionConfig(name="test-env", url="https://example.com", api_key_cmd="echo key")
    mocker.patch("dokli.logs_cli.resolve_connection", return_value=connection)
    client = _patch_logs_client(mocker)

    def fake_request(method, route, params):
        if route == "application.one":
            return _FakeResponse({"appName": "app-xyz"})
        if route == "docker.getContainersByAppNameMatch":
            return _FakeResponse([{"containerId": "cc1", "state": "running"}])
        raise AssertionError(route)

    client.request.side_effect = fake_request

    async def fake_stream(connection, endpoint, params):
        assert endpoint == "/docker-container-logs"
        assert params == {"containerId": "cc1", "tail": 100}
        yield "app live\r"

    mocker.patch("dokli.logs_cli.iter_lines", side_effect=fake_stream)
    result = CliRunner().invoke(app, ["logs", "test-env", "--application-id", "a1", "-f"])
    assert result.exit_code == 0
    assert "app live" in result.output


def test_logs_follow_deployment_uses_log_path(mocker):
    """We expect deployment logs -f to stream via the deployment logPath."""
    from typer.testing import CliRunner

    connection = ConnectionConfig(name="test-env", url="https://example.com", api_key_cmd="echo key")
    mocker.patch("dokli.logs_cli.resolve_connection", return_value=connection)
    client = _patch_logs_client(mocker)
    client.request.return_value = _FakeResponse([{"deploymentId": "d1", "logPath": "/tmp/x.log"}])

    async def fake_stream(connection, endpoint, params):
        assert endpoint == "/listen-deployment"
        assert params == {"logPath": "/tmp/x.log"}
        yield "dep live\r"

    mocker.patch("dokli.logs_cli.iter_lines", side_effect=fake_stream)
    result = CliRunner().invoke(app, ["logs", "test-env", "--deployment-id", "d1", "-f"])
    assert result.exit_code == 0
    assert "dep live" in result.output


def test_logs_requires_exactly_one_selector(mocker):
    """We expect logs to fail unless exactly one service selector is given."""
    from typer.testing import CliRunner

    connection = ConnectionConfig(name="test-env", url="https://example.com", api_key_cmd="echo key")
    mocker.patch("dokli.logs_cli.resolve_connection", return_value=connection)
    assert CliRunner().invoke(app, ["logs", "test-env"]).exit_code != 0
    assert CliRunner().invoke(app, ["logs", "test-env", "--compose-id", "c1", "--application-id", "a1"]).exit_code != 0


def test_logs_compose_requires_container_id(mocker):
    """We expect compose logs to require --container-id."""
    from typer.testing import CliRunner

    connection = ConnectionConfig(name="test-env", url="https://example.com", api_key_cmd="echo key")
    mocker.patch("dokli.logs_cli.resolve_connection", return_value=connection)
    result = CliRunner().invoke(app, ["logs", "test-env", "--compose-id", "c1"])
    assert result.exit_code != 0


def test_refresh_command_forces_refresh(mocker):
    """We expect refresh to force the schema refresh."""
    connection = ConnectionConfig(name="test-env", url="https://example.com", api_key_cmd="echo key")
    mocker.patch("dokli.cli._get_connection", return_value=connection)
    client = mocker.patch("dokli.cli.APIClient")

    refresh_command("test-env")

    client.assert_called_once_with(connection, force_refresh=True)


def test_tui_command_opens_connection_by_name(mocker):
    """We expect tui <name> to set the connection and run without the picker."""
    connection = ConnectionConfig(name="test-env", url="https://example.com", api_key_cmd="echo key")
    dokli.cli.tui.connection = None
    mocker.patch("dokli.cli._get_connection", return_value=connection)
    run = mocker.patch("dokli.cli.tui.run")

    tui_command("test-env")

    assert dokli.cli.tui.connection is connection
    run.assert_called_once_with()


def test_tui_command_without_name_keeps_picker(mocker):
    """We expect tui (no arg) to keep the interactive picker: no lookup, no connection."""
    get_connection = mocker.patch("dokli.cli._get_connection")
    run = mocker.patch("dokli.cli.tui.run")
    dokli.cli.tui.connection = None

    tui_command(None)

    get_connection.assert_not_called()
    assert dokli.cli.tui.connection is None
    run.assert_called_once_with()


def test_tui_command_unknown_name_raises(mocker):
    """We expect tui <unknown> to fail with a bad-parameter error."""
    mocker.patch("dokli.cli._get_connection", side_effect=typer.BadParameter("Unknown connection 'nope'."))

    with pytest.raises(typer.BadParameter):
        tui_command("nope")


def test_build_command_skips_broken_connection(mocker):
    """We expect a connection with an unresolvable key not to break the CLI."""
    good = ConnectionConfig(name="good", url="https://a.example.com", api_key="*" * 64)
    bad = ConnectionConfig(name="bad", url="https://b.example.com", api_key_cmd="secret-tool lookup dokli nope")

    def fake_register(connection):
        if connection.name == "bad":
            raise RuntimeError("api_key_cmd failed")
        return typer.Typer(name=connection.name)

    mocker.patch("dokli.openapi_cli._register_api_methods", side_effect=fake_register)
    app = typer.Typer()
    api_group = build_command(Config(connections=[good, bad]))
    app.add_typer(api_group)

    api_group = app.registered_groups[0].typer_instance
    names = [group.name for group in api_group.registered_groups]
    assert "good" in names
    assert "bad" not in names


def test_complete_connection_names_filters_by_prefix(mocker):
    """We expect completion to offer configured connections matching the prefix."""
    mocker.patch(
        "dokli.config.Config",
        return_value=Config(
            connections=[
                ConnectionConfig(name="alpha", url="https://alpha.lan", api_key_cmd="echo key"),
                ConnectionConfig(name="beta", url="https://test.lan", api_key_cmd="echo key"),
            ]
        ),
    )

    assert [item.value for item in complete_connection_names(None, None, "alph")] == ["alpha"]
    assert [item.value for item in complete_connection_names(None, None, "bet")] == ["beta"]
    assert complete_connection_names(None, None, "zzz") == []


def test_connection_arguments_expose_shell_complete():
    """We expect connection-name arguments to carry a shell_complete callback."""
    from typer.main import get_command

    group = get_command(app)
    for name in ("refresh", "state", "export", "schema", "tui"):
        command = group.get_command(None, name)
        param = next(p for p in command.params if p.name == "connection_name")
        assert param._custom_shell_complete is complete_connection_names


def test_connections_group_arguments_expose_shell_complete():
    """We expect connections subcommands to complete existing names."""
    from typer.main import get_command

    group = get_command(app).get_command(None, "connections")
    for name in ("update", "remove", "get", "test"):
        command = group.get_command(None, name)
        param = next(p for p in command.params if p.name == "name")
        assert param._custom_shell_complete is complete_connection_names
