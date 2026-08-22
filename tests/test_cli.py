"""Dokli CLI tests."""

import pytest
import typer

import dokli.cli
from dokli.cli import app, main, refresh_command, tui_command
from dokli.config import Config, ConnectionConfig, complete_connection_names
from dokli.openapi_cli import build_command
from dokli.stats_common import metrics_for, palette_for, stats_argv, stats_command_hint
from dokli.stats_cli import (
    _darken_color,
    _default_samples,
    _fill_from_history,
    _format_time,
    _header_with_range,
    _lighten_color,
    resolve_palette,
)


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


def _patch_logs_client(mocker):
    return mocker.patch("dokli.logs_cli.request_json")


def test_logs_one_shot_compose(mocker):
    """We expect compose logs without -f to hit compose.readLogs and exit."""
    from typer.testing import CliRunner

    connection = ConnectionConfig(name="test-env", url="https://example.com", api_key_cmd="echo key")
    mocker.patch("dokli.logs_cli.resolve_connection", return_value=connection)
    client = _patch_logs_client(mocker)
    client.return_value = "line a\nline b\n"

    result = CliRunner().invoke(
        app, ["logs", "test-env", "--compose-id", "c1", "--container-id", "cc1", "-n", "2"]
    )
    assert result.exit_code == 0
    assert "line a" in result.output
    assert "line b" in result.output
    _, route, params = client.call_args.args
    assert route == "compose.readLogs"
    assert params == {"composeId": "c1", "containerId": "cc1", "tail": 2}


def test_logs_one_shot_application(mocker):
    """We expect application logs without -f to hit application.readLogs."""
    from typer.testing import CliRunner

    connection = ConnectionConfig(name="test-env", url="https://example.com", api_key_cmd="echo key")
    mocker.patch("dokli.logs_cli.resolve_connection", return_value=connection)
    client = _patch_logs_client(mocker)
    client.return_value = "app line\n"

    result = CliRunner().invoke(app, ["logs", "test-env", "--application-id", "a1", "-n", "2"])
    assert result.exit_code == 0
    assert "app line" in result.output
    _, route, params = client.call_args.args
    assert route == "application.readLogs"
    assert params == {"applicationId": "a1", "tail": 2}


def test_logs_one_shot_deployment(mocker):
    """We expect deployment logs without -f to hit deployment.readLogs."""
    from typer.testing import CliRunner

    connection = ConnectionConfig(name="test-env", url="https://example.com", api_key_cmd="echo key")
    mocker.patch("dokli.logs_cli.resolve_connection", return_value=connection)
    client = _patch_logs_client(mocker)
    client.return_value = "dep line\n"

    result = CliRunner().invoke(app, ["logs", "test-env", "--deployment-id", "d1", "-n", "2"])
    assert result.exit_code == 0
    assert "dep line" in result.output
    _, route, params = client.call_args.args
    assert route == "deployment.readLogs"
    assert params == {"deploymentId": "d1", "tail": 2}


def test_logs_follow_compose_streams_ws(mocker):
    """We expect compose logs -f to stream the container WebSocket."""
    from typer.testing import CliRunner

    connection = ConnectionConfig(name="test-env", url="https://example.com", api_key_cmd="echo key")
    mocker.patch("dokli.logs_cli.resolve_connection", return_value=connection)
    client = _patch_logs_client(mocker)
    client.return_value = {"serverId": None}  # compose.one

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

    def fake_request(connection, route, params):
        if route == "application.one":
            return {"appName": "app-xyz", "serverId": "srv1"}
        if route == "docker.getContainersByAppNameMatch":
            assert params == {"appName": "app-xyz", "serverId": "srv1"}
            return [{"containerId": "cc1", "state": "running"}]
        raise AssertionError(route)

    client.side_effect = fake_request

    async def fake_stream(connection, endpoint, params):
        assert endpoint == "/docker-container-logs"
        assert params == {"containerId": "cc1", "tail": 100, "serverId": "srv1"}
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
    client.return_value = [{"deploymentId": "d1", "logPath": "/tmp/x.log", "serverId": "srv1"}]

    async def fake_stream(connection, endpoint, params):
        assert endpoint == "/listen-deployment"
        assert params == {"logPath": "/tmp/x.log", "serverId": "srv1"}
        yield "dep live\r"

    mocker.patch("dokli.logs_cli.iter_lines", side_effect=fake_stream)
    result = CliRunner().invoke(app, ["logs", "test-env", "--deployment-id", "d1", "-f"])
    assert result.exit_code == 0
    assert "dep live" in result.output


def test_logs_follow_stream_ends_cleanly(mocker):
    """We expect -f to exit cleanly when the WebSocket stream ends."""
    import websockets

    from typer.testing import CliRunner

    connection = ConnectionConfig(name="test-env", url="https://example.com", api_key_cmd="echo key")
    mocker.patch("dokli.logs_cli.resolve_connection", return_value=connection)
    client = _patch_logs_client(mocker)
    client.return_value = {"serverId": None}  # compose.one

    async def fake_stream(connection, endpoint, params):
        yield "line\r"
        raise websockets.exceptions.ConnectionClosedOK(None, None)

    mocker.patch("dokli.logs_cli.iter_lines", side_effect=fake_stream)
    result = CliRunner().invoke(app, ["logs", "test-env", "--compose-id", "c1", "--container-id", "cc1", "-f"])
    assert result.exit_code == 0
    assert "line" in result.output


def test_logs_follow_connection_error_exits_one(mocker):
    """We expect a failed WebSocket connection to exit non-zero with an error."""
    from typer.testing import CliRunner

    connection = ConnectionConfig(name="test-env", url="https://example.com", api_key_cmd="echo key")
    mocker.patch("dokli.logs_cli.resolve_connection", return_value=connection)
    client = _patch_logs_client(mocker)
    client.return_value = {"serverId": None}  # compose.one

    async def fake_stream(connection, endpoint, params):
        if False:
            yield  # make it an async generator
        raise OSError("connection refused")

    mocker.patch("dokli.logs_cli.iter_lines", side_effect=fake_stream)
    result = CliRunner().invoke(app, ["logs", "test-env", "--compose-id", "c1", "--container-id", "cc1", "-f"])
    assert result.exit_code == 1
    assert "Log stream failed" in result.output


def test_logs_validates_lines_range(mocker):
    """We expect -n outside the API's tail bounds to be rejected."""
    from typer.testing import CliRunner

    connection = ConnectionConfig(name="test-env", url="https://example.com", api_key_cmd="echo key")
    mocker.patch("dokli.logs_cli.resolve_connection", return_value=connection)
    result = CliRunner().invoke(app, ["logs", "test-env", "--deployment-id", "d1", "-n", "0"])
    assert result.exit_code != 0
    assert "must be between" in result.output
    result = CliRunner().invoke(app, ["logs", "test-env", "--deployment-id", "d1", "-n", "10001"])
    assert result.exit_code != 0


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


_STATS_T0 = "2026-08-20T07:00:00.000Z"
_STATS_T1 = "2026-08-20T07:00:01.000Z"
_STATS_SAMPLE = {
    "cpu": {"value": "0.20%", "time": _STATS_T0},
    "memory": {"value": {"used": "1.108GiB", "total": "62.4GiB"}, "time": _STATS_T0},
    "network": {"value": {"inputMb": "7.59", "outputMb": "0.14"}, "time": _STATS_T0},
    "block": {"value": {"readMb": "786", "writeMb": "1.31"}, "time": _STATS_T0},
    "disk": {"value": {"diskUsedPercentage": "42.0%", "total": "1024GB"}, "time": _STATS_T0},
}
#: One second later with advanced counters (1s delta -> deterministic rates).
_STATS_SAMPLE2 = {
    "cpu": {"value": "0.25%", "time": _STATS_T1},
    "memory": {"value": {"used": "1.108GiB", "total": "62.4GiB"}, "time": _STATS_T1},
    "network": {"value": {"inputMb": "7.79", "outputMb": "0.16"}, "time": _STATS_T1},
    "block": {"value": {"readMb": "786.5", "writeMb": "1.41"}, "time": _STATS_T1},
    "disk": {"value": {"diskUsedPercentage": "42.0%", "total": "1024GB"}, "time": _STATS_T1},
}


def _patch_stats_env(mocker):
    connection = ConnectionConfig(name="test-env", url="https://example.com", api_key_cmd="echo key")
    mocker.patch("dokli.stats_cli.resolve_connection", return_value=connection)
    mocker.patch("dokli.stats_cli.request_json")
    return connection


def test_stats_streams_compose(mocker):
    """We expect stats to resolve the compose then stream its container metrics."""
    from typer.testing import CliRunner

    _patch_stats_env(mocker)
    mocker.patch(
        "dokli.stats_cli.request_json",
        return_value={"appName": "app-xyz", "composeType": "docker-compose"},
    )

    async def fake_stream(connection, app_name, app_type):
        assert app_name == "app-xyz"
        assert app_type == "docker-compose"
        yield _STATS_SAMPLE
        yield _STATS_SAMPLE2

    mocker.patch("dokli.stats_cli.iter_stats", side_effect=fake_stream)
    result = CliRunner().invoke(app, ["stats", "test-env", "--compose-id", "c1"])
    assert result.exit_code == 0
    assert "test-env › app-xyz (docker-compose)" in result.output
    assert "CPU" in result.output
    assert "MEMORY" in result.output
    assert "0.20%" in result.output
    assert "1.108GiB/62.4GiB" in result.output
    assert "8MB\u2193/143KB\u2191" in result.output
    assert "\u2193" in result.output
    assert "DISK" not in result.output  # disk is only reported for system stats


def test_stats_backfills_history_into_header(mocker):
    """We expect the REST history to prime the charts and show a time range."""
    from typer.testing import CliRunner

    _patch_stats_env(mocker)
    mocker.patch(
        "dokli.stats_cli.request_json",
        side_effect=lambda connection, route, params: {
            "compose.one": {"appName": "app-xyz", "composeType": "docker-compose"},
            "application.readAppMonitoring": {
                "cpu": [
                    {"value": "1.0%", "time": "2026-08-20T10:00:00Z"},
                    {"value": "2.0%", "time": "2026-08-20T10:00:02Z"},
                ],
                "memory": [],
            },
        }.get(route, {}),
    )

    async def fake_stream(connection, app_name, app_type):
        yield _STATS_SAMPLE

    mocker.patch("dokli.stats_cli.iter_stats", side_effect=fake_stream)
    result = CliRunner().invoke(app, ["stats", "test-env", "--compose-id", "c1"])
    assert result.exit_code == 0
    assert "test-env › app-xyz (docker-compose) ·" in result.output


def test_stats_once_prints_single_snapshot(mocker):
    """We expect --once to render one sample and exit (no live stream)."""
    from typer.testing import CliRunner

    _patch_stats_env(mocker)
    mocker.patch(
        "dokli.stats_cli.request_json",
        side_effect=lambda connection, route, params: {
            "compose.one": {"appName": "app-xyz", "composeType": "docker-compose"},
            "application.readAppMonitoring": {},
        }.get(route, {}),
    )

    consumed = []

    async def fake_stream(connection, app_name, app_type):
        yield _STATS_SAMPLE
        yield _STATS_SAMPLE2  # --once must stop after the first sample.

    async def spy(connection, app_name, app_type):
        async for item in fake_stream(connection, app_name, app_type):
            consumed.append(item)
            yield item

    mocker.patch("dokli.stats_cli.iter_stats", side_effect=spy)
    result = CliRunner().invoke(app, ["stats", "test-env", "--compose-id", "c1", "--once"])
    assert result.exit_code == 0
    assert len(consumed) == 1
    assert "CPU" in result.output


def test_stats_agent_format_emits_dataframe(mocker):
    """We expect --format agent to emit a header row + one JSON row per sample."""
    import json

    from typer.testing import CliRunner

    _patch_stats_env(mocker)
    mocker.patch(
        "dokli.stats_cli.request_json",
        side_effect=lambda connection, route, params: {
            "compose.one": {"appName": "app-xyz", "composeType": "docker-compose"},
            "application.readAppMonitoring": {},
        }.get(route, {}),
    )

    async def fake_stream(connection, app_name, app_type):
        yield _STATS_SAMPLE

    mocker.patch("dokli.stats_cli.iter_stats", side_effect=fake_stream)
    result = CliRunner().invoke(app, ["stats", "test-env", "--compose-id", "c1", "--format", "agent", "--once"])
    assert result.exit_code == 0
    lines = result.output.strip().split("\n")
    header = json.loads(lines[0])
    assert header == [
        "time", "cpu", "memory", "network__down", "network__up", "block__down", "block__up", "disk",
    ]
    row = json.loads(lines[1])
    assert isinstance(row, list) and len(row) == len(header)


def test_stats_no_backfill_skips_history(mocker):
    """We expect --no-backfill to skip the REST history fetch."""
    from typer.testing import CliRunner

    _patch_stats_env(mocker)
    request = mocker.patch(
        "dokli.stats_cli.request_json",
        side_effect=lambda connection, route, params: {"compose.one": {"appName": "app-xyz", "composeType": "docker-compose"}}.get(route, {}),
    )

    async def fake_stream(connection, app_name, app_type):
        yield _STATS_SAMPLE

    mocker.patch("dokli.stats_cli.iter_stats", side_effect=fake_stream)
    result = CliRunner().invoke(app, ["stats", "test-env", "--compose-id", "c1", "--no-backfill"])
    assert result.exit_code == 0
    routes = set(call.args[1] for call in request.call_args_list)
    assert "application.readAppMonitoring" not in routes


def test_stats_header_includes_project(mocker):
    """We expect the context header to show the compose's project scope."""
    from typer.testing import CliRunner

    _patch_stats_env(mocker)
    mocker.patch(
        "dokli.stats_cli.request_json",
        return_value={
            "appName": "app-xyz",
            "composeType": "docker-compose",
            "environment": {"project": {"name": "agents"}},
        },
    )

    async def fake_stream(connection, app_name, app_type):
        yield _STATS_SAMPLE

    mocker.patch("dokli.stats_cli.iter_stats", side_effect=fake_stream)
    result = CliRunner().invoke(app, ["stats", "test-env", "--compose-id", "c1"])
    assert result.exit_code == 0
    assert "test-env › agents/app-xyz (docker-compose)" in result.output


def test_stats_application_resolves(mocker):
    """We expect stats to stream an application with the application appType."""
    from typer.testing import CliRunner

    _patch_stats_env(mocker)
    mocker.patch("dokli.stats_cli.request_json", return_value={"appName": "app-xyz"})

    async def fake_stream(connection, app_name, app_type):
        assert app_name == "app-xyz"
        assert app_type == "application"
        yield _STATS_SAMPLE

    mocker.patch("dokli.stats_cli.iter_stats", side_effect=fake_stream)
    result = CliRunner().invoke(app, ["stats", "test-env", "--application-id", "a1"])
    assert result.exit_code == 0
    assert "test-env › app-xyz (application)" in result.output
    assert "CPU" in result.output


def test_stats_defaults_to_system(mocker):
    """We expect stats with no selector to stream the host system stats."""
    from typer.testing import CliRunner

    _patch_stats_env(mocker)

    async def fake_stream(connection, app_name, app_type):
        assert app_name == "dokploy"
        assert app_type == "application"
        yield _STATS_SAMPLE
        yield _STATS_SAMPLE2

    mocker.patch("dokli.stats_cli.iter_stats", side_effect=fake_stream)
    result = CliRunner().invoke(app, ["stats", "test-env"])
    assert result.exit_code == 0
    assert "test-env › dokploy (system)" in result.output
    assert "CPU" in result.output
    assert "DISK" in result.output


def test_stats_rejects_multiple_selectors(mocker):
    """We expect more than one service selector to be rejected."""
    from typer.testing import CliRunner

    _patch_stats_env(mocker)
    result = CliRunner().invoke(app, ["stats", "test-env", "--compose-id", "c1", "--application-id", "a1"])
    assert result.exit_code != 0
    assert "at most one" in result.output


def test_stats_raw_app_name_and_type(mocker):
    """We expect --app-name/--app-type to stream raw appName/appType."""
    from typer.testing import CliRunner

    _patch_stats_env(mocker)

    async def fake_stream(connection, app_name, app_type):
        assert app_name == "blog-api"
        assert app_type == "stack"
        yield _STATS_SAMPLE

    mocker.patch("dokli.stats_cli.iter_stats", side_effect=fake_stream)
    result = CliRunner().invoke(app, ["stats", "test-env", "--app-name", "blog-api", "--app-type", "stack"])
    assert result.exit_code == 0
    assert "test-env › blog-api (stack)" in result.output


def test_stats_rejects_mixed_selector_and_app_name(mocker):
    """We expect --app-name/--app-type not to combine with a selector."""
    from typer.testing import CliRunner

    _patch_stats_env(mocker)
    result = CliRunner().invoke(app, ["stats", "test-env", "--compose-id", "c1", "--app-name", "foo"])
    assert result.exit_code != 0
    assert "cannot be combined" in result.output


def test_stats_validates_app_type(mocker):
    """We expect an unknown --app-type to be rejected."""
    from typer.testing import CliRunner

    _patch_stats_env(mocker)
    result = CliRunner().invoke(app, ["stats", "test-env", "--app-type", "bogus"])
    assert result.exit_code != 0
    # The option name may be colorized (ANSI) by typer, so match the stable part.
    assert "must be one of" in result.output


def test_stats_streams_container_by_name(mocker):
    """We expect stats to target a bare container by its docker name."""
    from typer.testing import CliRunner

    _patch_stats_env(mocker)

    async def fake_stream(connection, app_name, app_type):
        assert app_name == "qbittorrent"
        assert app_type == "docker-compose"
        yield _STATS_SAMPLE
        yield _STATS_SAMPLE2

    mocker.patch("dokli.stats_cli.iter_stats", side_effect=fake_stream)
    result = CliRunner().invoke(app, ["stats", "test-env", "--container-name", "qbittorrent"])
    assert result.exit_code == 0
    assert "test-env › qbittorrent (container)" in result.output
    assert "CPU" in result.output


def test_stats_container_by_id_resolves_name(mocker):
    """We expect stats to resolve a container id to its docker name."""
    from typer.testing import CliRunner

    _patch_stats_env(mocker)
    mocker.patch(
        "dokli.stats_cli.request_json",
        return_value=[{"containerId": "d205cc0de4be", "name": "qbittorrent", "state": "running"}],
    )

    async def fake_stream(connection, app_name, app_type):
        assert app_name == "qbittorrent"
        assert app_type == "docker-compose"
        yield _STATS_SAMPLE
        yield _STATS_SAMPLE2

    mocker.patch("dokli.stats_cli.iter_stats", side_effect=fake_stream)
    result = CliRunner().invoke(app, ["stats", "test-env", "--container-id", "d205cc0d"])
    assert result.exit_code == 0
    assert "test-env › qbittorrent (container)" in result.output
    assert "CPU" in result.output


def test_stats_container_id_without_match_fails(mocker):
    """We expect an unknown container id to be rejected."""
    from typer.testing import CliRunner

    _patch_stats_env(mocker)
    mocker.patch("dokli.stats_cli.request_json", return_value=[{"containerId": "d205cc0de4be", "name": "qbittorrent"}])

    result = CliRunner().invoke(app, ["stats", "test-env", "--container-id", "zzz999"])
    assert result.exit_code != 0
    assert "No running container matches" in result.output


class TestLightenColor:
    """Hex color lightening (used for the up half of two-direction graphs)."""

    def test_full_amount_goes_white(self):
        assert _lighten_color("#000000", 1.0) == "#ffffff"

    def test_zero_amount_is_unchanged(self):
        assert _lighten_color("#89dceb", 0.0) == "#89dceb"

    def test_white_is_unchanged(self):
        assert _lighten_color("#ffffff", 0.35) == "#ffffff"

    def test_subtle_lighten(self):
        # 0x89 = 137 -> 137 + (255-137)*0.35 = 178.3 -> round 178 -> 0xb2
        assert _lighten_color("#898989", 0.35) == "#b2b2b2"


class TestDarkenColor:
    """Hex color darkening (used for the down half of two-direction graphs)."""

    def test_full_amount_goes_black(self):
        assert _darken_color("#ffffff", 1.0) == "#000000"

    def test_zero_amount_is_unchanged(self):
        assert _darken_color("#cba6f7", 0.0) == "#cba6f7"

    def test_black_is_unchanged(self):
        assert _darken_color("#000000", 0.35) == "#000000"

    def test_subtle_darken(self):
        # 0xcb = 203 -> 203 * 0.65 = 131.95 -> round 132 -> 0x84
        assert _darken_color("#cbcbcb", 0.35) == "#848484"

    def test_dark_and_light_are_symmetric(self):
        # Lightening and darkening the same base by equal amounts differ.
        base = "#cba6f7"
        assert _lighten_color(base) != _darken_color(base)


def test_stats_validates_height_and_samples(mocker):
    """We expect out-of-range height/samples to be rejected."""
    from typer.testing import CliRunner

    _patch_stats_env(mocker)
    for extra in (["--height", "0"], ["--height", "9"], ["--samples", "0"]):
        result = CliRunner().invoke(app, ["stats", "test-env", "--compose-id", "c1", *extra])
        assert result.exit_code != 0


class TestDefaultSamples:
    """Adaptive default history based on console width."""

    def test_width_80(self):
        # 80 cols -> inner 78 -> 156 samples.
        assert _default_samples(80) == 156

    def test_wide_terminal(self):
        assert _default_samples(200) == 396

    def test_narrow_terminal_has_floor(self):
        assert _default_samples(3) == 10


class TestStatsTarget:
    """Building the ``dokli stats`` CLI args/hint from a target."""

    def test_system_argv(self):
        assert stats_argv("meche", "system") == ["stats", "meche"]

    def test_compose_argv(self):
        assert stats_argv("meche", "compose", "c1") == ["stats", "meche", "--compose-id", "c1"]

    def test_container_argv(self):
        assert stats_argv("meche", "container", "abc") == ["stats", "meche", "--container-id", "abc"]

    def test_hint_prepends_dokli(self):
        assert stats_command_hint("meche", "application", "a1") == "dokli stats meche --application-id a1"

    def test_metrics_omit_disk_outside_system(self):
        assert "disk" in metrics_for("system")
        assert "disk" not in metrics_for("container")


class TestPalette:
    """Theme-resolution for the stats render."""

    def test_dark_uses_mocha(self):
        assert palette_for(True).metric_colors["cpu"] == "#89dceb"
        assert palette_for(True).border_color == "#6c7086"

    def test_light_uses_latte(self):
        assert palette_for(False).metric_colors["cpu"] == "#04a5e5"
        assert palette_for(False).metric_colors["network"] == "#df8e1d"
        assert palette_for(False).border_color == "#6c6f85"

    def test_resolve_env_light(self, monkeypatch):
        monkeypatch.setenv("DOKLI_THEME", "light")
        metric_colors, border = resolve_palette()
        assert metric_colors["memory"] == "#40a02b"
        assert border == "#6c6f85"

    def test_resolve_env_default_dark(self, monkeypatch):
        monkeypatch.delenv("DOKLI_THEME", raising=False)
        metric_colors, _ = resolve_palette()
        assert metric_colors["disk"] == "#f38ba8"


class TestHistoryBackfill:
    """Priming buffers and the header time range from the REST history."""

    def test_fill_primes_buffers_in_order(self):
        from collections import deque

        history = {
            "cpu": [
                {"value": "1.0%", "time": "2026-08-20T10:00:00Z"},
                {"value": "2.0%", "time": "2026-08-20T10:00:01Z"},
                {"value": "3.0%", "time": "2026-08-20T10:00:02Z"},
            ],
            "network": [
                {"value": {"inputMb": "1", "outputMb": "1"}, "time": "2026-08-20T10:00:00Z"},
                {"value": {"inputMb": "3", "outputMb": "2"}, "time": "2026-08-20T10:00:02Z"},
            ],
        }
        buffers: dict = {}
        duo_buffers: dict[str, tuple[deque, deque]] = {
            "network": (deque(), deque()),
            "block": (deque(), deque()),
        }
        timestamps: dict[str, deque] = {}
        _fill_from_history(history, buffers, duo_buffers, timestamps, ("cpu", "network"), samples=10)
        assert "disk" not in buffers
        assert buffers["cpu"] == deque([1.0, 2.0, 3.0])
        down = list(duo_buffers["network"][0])
        up = list(duo_buffers["network"][1])
        assert down == [1.0, 3.0]
        assert up == [1.0, 2.0]
        assert list(timestamps["cpu"]) == ["2026-08-20T10:00:00Z", "2026-08-20T10:00:01Z", "2026-08-20T10:00:02Z"]

    def test_format_time_local(self):
        assert _format_time("2026-08-20T10:00:00Z") is not None

    def test_header_with_range(self):
        header = _header_with_range("me › dokploy (system)", ("10:00:00", "10:00:02"))
        assert "10:00:00→10:00:02" in header

    def test_visible_range_from_timestamps(self):
        from collections import deque

        from dokli.stats_cli import _visible_range

        timestamps = {
            "cpu": deque(["2026-08-20T10:00:00Z", "2026-08-20T10:00:01Z"]),
            "memory": deque(["2026-08-20T10:00:01Z", "2026-08-20T10:00:02Z"]),
        }
        start, end = _visible_range(timestamps)
        assert start is not None and start.endswith("00:00")
        assert end is not None and end.endswith("00:02")


class TestStatsLoading:
    """The loading frame keeps the box layout."""

    def test_loading_frame_prints_loading(self, capsys):
        from dokli.stats_cli import _print_loading

        _print_loading("me › x (system)", ("cpu", "memory"), height=1)
        out = capsys.readouterr().out
        assert "loading…" in out
        assert "CPU" in out
        assert "MEMORY" in out


def test_stats_stream_ends_cleanly(mocker):
    """We expect stats to exit cleanly when the WebSocket stream ends."""
    import websockets

    from typer.testing import CliRunner

    _patch_stats_env(mocker)
    mocker.patch(
        "dokli.stats_cli.request_json",
        return_value={"appName": "app-xyz", "composeType": "docker-compose"},
    )

    async def fake_stream(connection, app_name, app_type):
        yield _STATS_SAMPLE
        raise websockets.exceptions.ConnectionClosedOK(None, None)

    mocker.patch("dokli.stats_cli.iter_stats", side_effect=fake_stream)
    result = CliRunner().invoke(app, ["stats", "test-env", "--compose-id", "c1"])
    assert result.exit_code == 0
    assert "CPU" in result.output


def test_stats_connection_error_exits_one(mocker):
    """We expect a failed stats WebSocket to exit non-zero with an error."""
    from typer.testing import CliRunner

    _patch_stats_env(mocker)
    mocker.patch(
        "dokli.stats_cli.request_json",
        return_value={"appName": "app-xyz", "composeType": "docker-compose"},
    )

    async def fake_stream(connection, app_name, app_type):
        if False:
            yield  # make it an async generator
        raise OSError("connection refused")

    mocker.patch("dokli.stats_cli.iter_stats", side_effect=fake_stream)
    result = CliRunner().invoke(app, ["stats", "test-env", "--compose-id", "c1"])
    assert result.exit_code == 1
    assert "Stats stream failed" in result.output


def test_stats_requires_app_name(mocker):
    """We expect a compose without an appName to be rejected."""
    from typer.testing import CliRunner

    _patch_stats_env(mocker)
    mocker.patch("dokli.stats_cli.request_json", return_value={"composeType": "docker-compose"})

    async def fake_stream(connection, app_name, app_type):
        yield _STATS_SAMPLE

    mocker.patch("dokli.stats_cli.iter_stats", side_effect=fake_stream)
    result = CliRunner().invoke(app, ["stats", "test-env", "--compose-id", "c1"])
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
    """We expect tui (no arg, no default) to keep the interactive picker."""
    get_connection = mocker.patch("dokli.cli._get_connection")
    run = mocker.patch("dokli.cli.tui.run")
    dokli.cli.tui.connection = None
    mocker.patch("dokli.cli.state", {"config": mocker.Mock(default_connection=None)})

    tui_command(None)

    get_connection.assert_not_called()
    assert dokli.cli.tui.connection is None
    run.assert_called_once_with()


def test_tui_command_without_name_uses_default(mocker):
    """We expect tui (no arg) to use the configured default connection."""
    get_connection = mocker.patch("dokli.cli._get_connection")
    run = mocker.patch("dokli.cli.tui.run")
    mocker.patch("dokli.cli.state", {"config": mocker.Mock(default_connection="meche")})

    tui_command(None)

    get_connection.assert_called_once_with(None)


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


def test_ls_lists_services(mocker):
    """We expect ls to list services across projects/environments."""
    from typer.testing import CliRunner

    from dokli.state import LiveEnvironment, LiveProject, LiveService, State

    connection = ConnectionConfig(name="test-env", url="https://example.com", api_key_cmd="echo key")
    mocker.patch("dokli.ls_cli.resolve_connection", return_value=connection)
    mocker.patch("dokli.ls_cli.APIClient", return_value=mocker.Mock())
    mocker.patch(
        "dokli.ls_cli.collect_state",
        return_value=State(
            connection="test-env",
            projects=[
                LiveProject(
                    project_id="p1",
                    name="media",
                    environments=[
                        LiveEnvironment(
                            environment_id="e1",
                            name="production",
                            is_default=True,
                            services=[
                                LiveService(service_id="c1", app_name="frigate-app", type="compose", name="frigate"),
                                LiveService(
                                    service_id="a1", app_name="web-app", type="application", name="web"
                                ),
                            ],
                        )
                    ],
                )
            ],
        ),
    )
    result = CliRunner().invoke(app, ["ls", "test-env"])
    assert result.exit_code == 0
    assert "frigate" in result.output
    assert "web" in result.output
    assert "c1" in result.output
    assert "a1" in result.output


def test_ls_filters_by_type_and_search(mocker):
    """We expect --type and --search to filter the listing."""
    from typer.testing import CliRunner

    from dokli.state import LiveEnvironment, LiveProject, LiveService, State

    connection = ConnectionConfig(name="test-env", url="https://example.com", api_key_cmd="echo key")
    mocker.patch("dokli.ls_cli.resolve_connection", return_value=connection)
    mocker.patch("dokli.ls_cli.APIClient", return_value=mocker.Mock())
    mocker.patch(
        "dokli.ls_cli.collect_state",
        return_value=State(
            connection="test-env",
            projects=[
                LiveProject(
                    project_id="p1",
                    name="media",
                    environments=[
                        LiveEnvironment(
                            environment_id="e1",
                            name="production",
                            is_default=True,
                            services=[
                                LiveService(service_id="c1", app_name="frigate-app", type="compose", name="frigate"),
                                LiveService(
                                    service_id="a1", app_name="web-app", type="application", name="web"
                                ),
                            ],
                        )
                    ],
                )
            ],
        ),
    )
    result = CliRunner().invoke(app, ["ls", "test-env", "--type", "application"])
    assert result.exit_code == 0
    assert "frigate" not in result.output
    assert "web" in result.output

    result = CliRunner().invoke(app, ["ls", "test-env", "--search", "frigate"])
    assert result.exit_code == 0
    assert "frigate" in result.output
    assert "web" not in result.output


def test_ls_agent_format_emits_dataframe(mocker):
    """We expect ls --format agent to emit a header row + one row per service."""
    import json

    from typer.testing import CliRunner

    from dokli.state import LiveEnvironment, LiveProject, LiveService, State

    connection = ConnectionConfig(name="test-env", url="https://example.com", api_key_cmd="echo key")
    mocker.patch("dokli.ls_cli.resolve_connection", return_value=connection)
    mocker.patch("dokli.ls_cli.APIClient", return_value=mocker.Mock())
    mocker.patch(
        "dokli.ls_cli.collect_state",
        return_value=State(
            connection="test-env",
            projects=[
                LiveProject(
                    project_id="p1",
                    name="media",
                    environments=[
                        LiveEnvironment(
                            environment_id="e1",
                            name="production",
                            is_default=True,
                            services=[LiveService(service_id="c1", app_name="frigate-app", type="compose", name="frigate")],
                        )
                    ],
                )
            ],
        ),
    )
    result = CliRunner().invoke(app, ["ls", "test-env", "--format", "agent"])
    assert result.exit_code == 0
    lines = result.output.strip().split("\n")
    assert json.loads(lines[0]) == ["project", "environment", "type", "name", "app_name", "id"]
    assert json.loads(lines[1]) == ["media", "production", "compose", "frigate", "frigate-app", "c1"]


def test_state_agent_format_emits_per_service_rows(mocker):
    """We expect state --format agent to emit per-service rows, no blobs."""
    import json

    from typer.testing import CliRunner

    from dokli.state import LiveEnvironment, LiveProject, LiveService, State

    connection = ConnectionConfig(name="test-env", url="https://example.com", api_key_cmd="echo key")
    mocker.patch("dokli.cli._get_connection", return_value=connection)
    mocker.patch(
        "dokli.cli.collect_state",
        return_value=State(
            connection="test-env",
            projects=[
                LiveProject(
                    project_id="p1",
                    name="media",
                    environments=[
                        LiveEnvironment(
                            environment_id="e1",
                            name="production",
                            is_default=True,
                            services=[LiveService(service_id="c1", app_name="frigate-app", type="compose", name="frigate")],
                        )
                    ],
                )
            ],
        ),
    )
    result = CliRunner().invoke(app, ["state", "test-env", "--format", "agent"])
    assert result.exit_code == 0
    lines = result.output.strip().split("\n")
    header = json.loads(lines[0])
    assert "project__name" in header
    assert "compose_file" not in "".join(lines)
    assert json.loads(lines[1])[header.index("name")] == "frigate"
