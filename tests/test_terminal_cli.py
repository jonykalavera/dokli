"""Terminal CLI tests: target validation and the stdin/socket bridge."""

import asyncio

from dokli.config import ConnectionConfig
from dokli.terminal_cli import (
    DEFAULT_COLS,
    DEFAULT_ROWS,
    _bridge,
    _read_stdin,
    _read_socket,
    _send_resize,
    _terminal_size,
    build_command,
    resize_message,
)
from dokli.wss import CONTAINER_TERMINAL_ENDPOINT, HOST_TERMINAL_ENDPOINT, open_terminal


def _connection() -> ConnectionConfig:
    return ConnectionConfig(name="test-env", url="https://example.com", api_key_cmd="echo key")


class FakeWebSocket:
    """A fake bidirectional WebSocket connection."""

    def __init__(self):
        self.sent = []
        self.incoming = []

    def __aiter__(self):
        return self

    async def __anext__(self):
        if not self.incoming:
            raise StopAsyncIteration
        return self.incoming.pop(0)

    async def send(self, data):
        self.sent.append(data)


class TestResizeMessage:
    """Resize control envelope tests."""

    def test_resize_message_is_json(self):
        """We expect a resize message to be a JSON control envelope."""
        import json

        msg = resize_message(120, 40)
        assert json.loads(msg) == {"type": "resize", "cols": 120, "rows": 40}


class TestTerminalSize:
    """Terminal size measurement tests."""

    def test_falls_back_to_defaults(self, monkeypatch):
        """We expect a failure measuring the terminal to fall back to defaults."""
        monkeypatch.setattr("dokli.terminal_cli.termios.tcgetattr", lambda fd: (_ for _ in ()).throw(OSError))
        cols, rows = _terminal_size()
        assert (cols, rows) == (DEFAULT_COLS, DEFAULT_ROWS)


class TestBridge:
    """Bidirectional stdin/socket bridge tests."""

    def test_forwards_stdin_and_socket(self, mocker, monkeypatch):
        """We expect stdin bytes to reach the socket and socket bytes to reach stdout."""
        ws = FakeWebSocket()
        ws.incoming = [b"prompt> "]
        stdin = mocker.Mock()
        stdin.isatty.return_value = False
        stdin.fileno.return_value = 3
        monkeypatch.setattr("dokli.terminal_cli.sys.stdin", stdin)
        monkeypatch.setattr("dokli.terminal_cli.os.read", lambda fd, n: b"")  # EOF immediately
        write = mocker.Mock()
        monkeypatch.setattr("dokli.terminal_cli._write_stdout", write)

        asyncio.run(_bridge(ws))
        assert write.call_args.args[0] == b"prompt> "

    def test_stdin_forwarded_as_binary(self, mocker, monkeypatch):
        """We expect stdin keystrokes to be sent as binary frames."""
        ws = FakeWebSocket()
        stdin = mocker.Mock()
        stdin.isatty.return_value = False
        stdin.fileno.return_value = 3
        monkeypatch.setattr("dokli.terminal_cli.sys.stdin", stdin)
        reads = iter([b"hello\r", b""])
        monkeypatch.setattr("dokli.terminal_cli.os.read", lambda fd, n: next(reads))

        asyncio.run(_read_stdin(ws))
        assert ws.sent == [b"hello\r"]

    def test_socket_output_forwarded(self, mocker, monkeypatch):
        """We expect socket frames to be written to stdout."""
        ws = FakeWebSocket()
        ws.incoming = [b"a", b"b\x1b[2J"]
        write = mocker.Mock()
        monkeypatch.setattr("dokli.terminal_cli._write_stdout", write)

        asyncio.run(_read_socket(ws))
        assert b"".join(call.args[0] for call in write.call_args_list) == b"ab\x1b[2J"

    def test_send_resize_uses_current_size(self, mocker, monkeypatch):
        """We expect SIGWINCH to send a resize message with the current size."""
        ws = FakeWebSocket()
        monkeypatch.setattr("dokli.terminal_cli._terminal_size", lambda: (140, 50))

        async def run():
            loop = asyncio.get_running_loop()
            _send_resize(ws)
            await asyncio.sleep(0.01)
            return ws.sent

        assert asyncio.run(run()) == ['{"type": "resize", "cols": 140, "rows": 50}']


class TestTerminalCommand:
    """dokli terminal argument validation and endpoint selection."""

    def _invoke(self, monkeypatch, *args):
        from typer.testing import CliRunner

        from dokli.cli import app

        import dokli.terminal_cli

        opened = {}

        async def fake_open(connection, path, params):
            opened["path"] = path
            opened["params"] = params
            ws = FakeWebSocket()
            return ws

        monkeypatch.setattr(dokli.terminal_cli, "open_terminal", fake_open)
        monkeypatch.setattr(dokli.terminal_cli, "resolve_connection", lambda config, name: _connection())
        monkeypatch.setattr(dokli.terminal_cli, "_bridge", lambda ws: asyncio.sleep(0))
        result = CliRunner().invoke(app, ["terminal", *args])
        return result, opened

    def test_requires_exactly_one_target(self, monkeypatch):
        """We expect exactly one of --container-id/--server-id to be required."""
        result, _ = self._invoke(monkeypatch, "test-env")
        assert result.exit_code == 2
        result, _ = self._invoke(monkeypatch, "test-env", "--container-id", "c1", "--server-id", "local")
        assert result.exit_code == 2

    def test_host_requires_username(self, monkeypatch):
        """We expect a host terminal to require --username."""
        result, _ = self._invoke(monkeypatch, "test-env", "--server-id", "local")
        assert result.exit_code == 2
        assert "is required for a host terminal" in result.output

    def test_container_target_uses_container_endpoint(self, monkeypatch):
        """We expect a container terminal to hit the container endpoint."""
        result, opened = self._invoke(
            monkeypatch, "test-env", "--container-id", "abc123", "--shell", "bash", "--service-id", "s1"
        )
        assert result.exit_code == 0
        assert opened["path"] == CONTAINER_TERMINAL_ENDPOINT
        assert opened["params"]["containerId"] == "abc123"
        assert opened["params"]["activeWay"] == "bash"
        assert opened["params"]["serviceId"] == "s1"

    def test_host_target_uses_host_endpoint(self, monkeypatch):
        """We expect a host terminal to hit the host endpoint with SSH params."""
        result, opened = self._invoke(monkeypatch, "test-env", "--server-id", "local", "--username", "root")
        assert result.exit_code == 0
        assert opened["path"] == HOST_TERMINAL_ENDPOINT
        assert opened["params"]["serverId"] == "local"
        assert opened["params"]["username"] == "root"
        assert opened["params"]["port"] == 22
