"""Terminal CLI tests: target validation and the stdin/socket bridge."""

import asyncio

import pytest

from dokli.config import ConnectionConfig
from dokli.terminal_cli import (
    DEFAULT_COLS,
    DEFAULT_ROWS,
    _bridge,
    _is_exit_line,
    _parse_command_result,
    _partial_output,
    _read_stdin,
    _read_socket,
    _run_remote_command,
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
        self.closed = False

    def __aiter__(self):
        return self

    async def __anext__(self):
        if not self.incoming:
            raise StopAsyncIteration
        return self.incoming.pop(0)

    async def recv(self):
        """Return the next queued frame, or time out when none is available."""
        if not self.incoming:
            raise asyncio.TimeoutError
        return self.incoming.pop(0)

    async def send(self, data):
        self.sent.append(data)

    async def close(self):
        self.closed = True


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

    def test_exit_line_closes_socket(self, mocker, monkeypatch):
        """We expect an exit line to force-close the socket."""
        ws = FakeWebSocket()
        stdin = mocker.Mock()
        stdin.isatty.return_value = False
        stdin.fileno.return_value = 3
        monkeypatch.setattr("dokli.terminal_cli.sys.stdin", stdin)
        reads = iter([b"exit\r", b""])
        monkeypatch.setattr("dokli.terminal_cli.os.read", lambda fd, n: next(reads))
        close = mocker.Mock()
        monkeypatch.setattr("dokli.terminal_cli._close_socket", close)

        asyncio.run(_read_stdin(ws))
        assert ws.sent == [b"exit\r"]
        assert close.called

    def test_non_exit_line_keeps_socket(self, mocker, monkeypatch):
        """We expect a non-exit line not to close the socket."""
        ws = FakeWebSocket()
        stdin = mocker.Mock()
        stdin.isatty.return_value = False
        stdin.fileno.return_value = 3
        monkeypatch.setattr("dokli.terminal_cli.sys.stdin", stdin)
        reads = iter([b"echo exit\r", b""])
        monkeypatch.setattr("dokli.terminal_cli.os.read", lambda fd, n: next(reads))
        close = mocker.Mock()
        monkeypatch.setattr("dokli.terminal_cli._close_socket", close)

        asyncio.run(_read_stdin(ws))
        assert not close.called


class TestIsExitLine:
    """Exit-line detection tests."""

    def test_exit_line(self):
        """We expect word-exact exit to be recognized."""
        assert _is_exit_line(b"exit")
        assert _is_exit_line(b"exit\r")
        assert _is_exit_line(b"logout")
        assert _is_exit_line(b"quit")

    def test_ctrl_d_is_exit(self):
        """We expect Ctrl+D (0x04) to be recognized as EOF."""
        assert _is_exit_line(b"\x04")
        assert _is_exit_line(b"\x04\r")

    def test_embedded_exit_is_not(self):
        """We expect 'echo exit' to not be an exit line."""
        assert not _is_exit_line(b"echo exit")
        assert not _is_exit_line(b"exits")

    def test_surrounding_whitespace_is_stripped(self):
        """We expect leading/trailing whitespace around exit to still match."""
        assert _is_exit_line(b" exit ")
        assert _is_exit_line(b"  exit")
        assert _is_exit_line(b"exit  ")
        assert _is_exit_line(b"\tquit \r\n")


class TestCloseSocket:
    """Force-close of the terminal socket (no close-handshake wait)."""

    def test_closes_transport(self, mocker):
        """We expect _close_socket to close the underlying transport."""
        from dokli.terminal_cli import _close_socket

        transport = mocker.Mock()
        ws = mocker.Mock(transport=transport)
        _close_socket(ws)
        transport.close.assert_called_once()

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

    def test_tty_session_shows_exit_hint(self, mocker, monkeypatch):
        """We expect a TTY session to print a red exit hint to stderr."""
        from dokli.terminal_cli import _run_terminal

        class TtyStdin:
            def isatty(self):
                return True

        async def fake_open(*a, **k):
            return FakeWebSocket()

        monkeypatch.setattr("sys.stdin", TtyStdin())
        monkeypatch.setattr("dokli.terminal_cli.open_terminal", fake_open)
        monkeypatch.setattr("dokli.terminal_cli._bridge", lambda ws: asyncio.sleep(0))
        rprint = mocker.patch("dokli.terminal_cli.rprint")
        asyncio.run(_run_terminal(_connection(), "abc123", None, "bash", None, None, None))
        assert rprint.called
        assert "exit" in rprint.call_args.args[0]

    def test_pipe_session_no_hint(self, mocker, monkeypatch):
        """We expect a non-TTY session to skip the exit hint."""
        from dokli.terminal_cli import _run_terminal

        class PipeStdin:
            def isatty(self):
                return False

        async def fake_open(*a, **k):
            return FakeWebSocket()

        monkeypatch.setattr("sys.stdin", PipeStdin())
        monkeypatch.setattr("dokli.terminal_cli.open_terminal", fake_open)
        monkeypatch.setattr("dokli.terminal_cli._bridge", lambda ws: asyncio.sleep(0))
        rprint = mocker.patch("dokli.terminal_cli.rprint")
        asyncio.run(_run_terminal(_connection(), "abc123", None, "bash", None, None, None))
        assert not rprint.called

    def test_command_one_shot_exit_code(self, mocker, monkeypatch):
        """We expect --command to skip the bridge and propagate the remote exit code."""
        from typer.testing import CliRunner

        from dokli.cli import app

        import dokli.terminal_cli

        async def fake_one_shot(*args):
            return 7

        bridge = mocker.Mock()
        monkeypatch.setattr(dokli.terminal_cli, "_run_one_shot", fake_one_shot)
        monkeypatch.setattr(dokli.terminal_cli, "_bridge", bridge)
        monkeypatch.setattr(dokli.terminal_cli, "resolve_connection", lambda config, name: _connection())
        result = CliRunner().invoke(app, ["terminal", "test-env", "--container-id", "c1", "--command", "echo hi"])
        assert result.exit_code == 7
        assert not bridge.called

    def test_command_still_requires_exactly_one_target(self, monkeypatch):
        """We expect --command to enforce the exactly-one-target validation."""
        result, _ = self._invoke(monkeypatch, "test-env", "--command", "echo hi")
        assert result.exit_code == 2
        result, _ = self._invoke(
            monkeypatch, "test-env", "--container-id", "c1", "--server-id", "local", "--command", "echo hi"
        )
        assert result.exit_code == 2

    def test_empty_command_rejected(self, monkeypatch):
        """We expect an empty --command to be a usage error without opening a socket."""
        result, opened = self._invoke(monkeypatch, "test-env", "--container-id", "c1", "--command", "")
        assert result.exit_code == 2
        assert "must not be empty" in result.output
        assert opened == {}


class TestParseCommandResult:
    """Sentinel output parsing tests."""

    START = "__DOKLI_START_tok"
    END = "__DOKLI_EXIT_tok"

    def test_clean_output_and_code(self):
        """We expect the captured output and exit code between the markers."""
        buffer = (
            f"printf '\\n{self.START}\\n'; {{ echo hi; }} 2>&1; printf '\\n{self.END}:%s\\n' \"$?\"\r\n"
            f"{self.START}\r\n"
            "hi\r\n"
            f"{self.END}:0\r\n"
        ).encode()
        assert _parse_command_result(buffer, self.START, self.END) == ("hi", 0)

    def test_crlf_is_normalized(self):
        """We expect CRLF line endings in the output normalized to LF."""
        buffer = (f"{self.START}\r\na\r\nb\r\nc\r\n{self.END}:3\r\n").encode()
        assert _parse_command_result(buffer, self.START, self.END) == ("a\nb\nc", 3)

    def test_echoed_preamble_is_ignored(self):
        """We expect the echoed input line (containing the marker literals) ignored."""
        echo = f"printf '\\n{self.START}\\n'; {{ echo hi; }} 2>&1; printf '\\n{self.END}:%s\\n' \"$?\""
        buffer = f"{echo}\r\n{self.START}\r\nhi\r\n{self.END}:0\r\n".encode()
        assert _parse_command_result(buffer, self.START, self.END) == ("hi", 0)

    def test_last_start_marker_wins(self):
        """We expect a wrapped echo's earlier standalone start line to be ignored."""
        echo = (
            f"{self.START}\r\n"
            f"printf '\\n{self.START}\\n'; ( echo hi ) 2>&1; printf '\\n{self.END}:%s\\n' \"$?\"\r\n"
        )
        buffer = f"{echo}{self.START}\r\nhi\r\n{self.END}:0\r\n".encode()
        assert _parse_command_result(buffer, self.START, self.END) == ("hi", 0)

    def test_missing_end_marker_returns_none(self):
        """We expect None while the end marker has not arrived."""
        buffer = f"{self.START}\r\nstill running\r\n".encode()
        assert _parse_command_result(buffer, self.START, self.END) is None


class TestRunRemoteCommand:
    """One-shot remote command over the terminal socket."""

    def test_sends_binary_payload_and_parses_exit_code(self, mocker, monkeypatch):
        """We expect a binary sentinel payload and the parsed remote exit code."""
        import dokli.terminal_cli

        monkeypatch.setattr("dokli.terminal_cli.secrets.token_hex", lambda n: "abc123def456")
        start = "__DOKLI_START_abc123def456__"
        end = "__DOKLI_EXIT_abc123def456__"
        stream = (
            f"printf '\\n{start}\\n'; ( echo hi ) 2>&1; printf '\\n{end}:%s\\n' \"$?\"\r\n"
            f"{start}\r\n"
            "hi\r\n"
            f"{end}:0\r\n"
        ).encode()
        ws = FakeWebSocket()
        ws.incoming = [stream[i : i + 7] for i in range(0, len(stream), 7)]
        close = mocker.Mock()
        monkeypatch.setattr("dokli.terminal_cli._close_socket", close)

        code = asyncio.run(_run_remote_command(ws, "echo hi"))

        assert code == 0
        assert isinstance(ws.sent[0], bytes)
        assert b"( echo hi )" in ws.sent[0]
        assert b"{ echo hi" not in ws.sent[0]
        assert b"[ -z" in ws.sent[0]
        assert b"DOKLI_abc123def456" in ws.sent[0]
        assert start.encode() in ws.sent[0]
        assert end.encode() in ws.sent[0]
        assert close.called

    def test_resends_payload_until_shell_attaches(self, mocker, monkeypatch):
        """We expect the payload resent until the shell is attached, running once."""
        monkeypatch.setattr("dokli.terminal_cli.secrets.token_hex", lambda n: "abc123def456")
        monkeypatch.setattr("dokli.terminal_cli._RESEND_INTERVAL", 0.01)
        start = "__DOKLI_START_abc123def456__"
        end = "__DOKLI_EXIT_abc123def456__"
        stream = (
            f"printf '\\n{start}\\n'; ( echo hi ) 2>&1; printf '\\n{end}:%s\\n' \"$?\"\r\n"
            f"{start}\r\n"
            "hi\r\n"
            f"{end}:0\r\n"
        ).encode()

        class SlowWebSocket(FakeWebSocket):
            """Fake socket whose first recv times out before the shell attaches."""

            def __init__(self):
                super().__init__()
                self.recv_calls = 0

            async def recv(self):
                self.recv_calls += 1
                if self.recv_calls == 1 or not self.incoming:
                    raise asyncio.TimeoutError
                return self.incoming.pop(0)

        ws = SlowWebSocket()
        ws.incoming = [stream]
        close = mocker.Mock()
        monkeypatch.setattr("dokli.terminal_cli._close_socket", close)

        code = asyncio.run(_run_remote_command(ws, "echo hi"))

        assert code == 0
        assert len(ws.sent) >= 2
        assert all(isinstance(frame, bytes) for frame in ws.sent)
        assert close.called

    def test_timeout_flushes_partial_output(self, mocker, monkeypatch, capsys):
        """We expect already-received output flushed before the timeout error."""
        import typer

        monkeypatch.setattr("dokli.terminal_cli._RESEND_INTERVAL", 0.01)
        close = mocker.Mock()
        monkeypatch.setattr("dokli.terminal_cli._close_socket", close)

        class PartialWebSocket(FakeWebSocket):
            """Yields one partial frame, then times out immediately forever."""

            def __init__(self):
                super().__init__()
                self.incoming = [b"\x1b[31mAuthentication failed: Please run ssh-add\x1b[0m\r\n"]

            async def recv(self):
                if self.incoming:
                    return self.incoming.pop(0)
                raise asyncio.TimeoutError

            async def send(self, data):
                # Count only: immediate timeouts spin many resends, so don't store them.
                self.sent_count = getattr(self, "sent_count", 0) + 1

        ws = PartialWebSocket()
        with pytest.raises(typer.Exit):
            asyncio.run(_run_remote_command(ws, "echo hi", timeout=0.2))

        assert "Authentication failed: Please run ssh-add" in capsys.readouterr().out
        close.assert_called_once()

    def test_connection_closed_flushes_partial_and_closes(self, mocker, monkeypatch, capsys):
        """We expect partial output flushed and the socket closed on early close."""
        import typer
        import websockets

        close = mocker.Mock()
        monkeypatch.setattr("dokli.terminal_cli._close_socket", close)

        class ClosingWebSocket(FakeWebSocket):
            """Yields one partial frame, then reports a closed connection."""

            def __init__(self):
                super().__init__()
                self.calls = 0

            async def recv(self):
                self.calls += 1
                if self.calls == 1:
                    return b"remote error line\r\n"
                raise websockets.exceptions.ConnectionClosed(None, None)

        ws = ClosingWebSocket()
        with pytest.raises(typer.Exit):
            asyncio.run(_run_remote_command(ws, "echo hi", timeout=0.5))

        close.assert_called_once()
        assert "remote error line" in capsys.readouterr().out

    def test_end_marker_split_across_frames(self, mocker, monkeypatch):
        """We expect the end marker parsed when split across two recv frames."""
        monkeypatch.setattr("dokli.terminal_cli.secrets.token_hex", lambda n: "abc123def456")
        start = "__DOKLI_START_abc123def456__"
        end = "__DOKLI_EXIT_abc123def456__"
        ws = FakeWebSocket()
        ws.incoming = [f"{start}\r\nhi\r\n{end}:".encode(), b"0\r\n"]
        close = mocker.Mock()
        monkeypatch.setattr("dokli.terminal_cli._close_socket", close)

        code = asyncio.run(_run_remote_command(ws, "echo hi"))

        assert code == 0
        close.assert_called_once()


class TestPartialOutput:
    """Best-effort output cleanup before reporting a failure."""

    def test_strips_echo_markers_ansi_and_crlf(self):
        """We expect echo/marker/ANSI lines removed and real lines kept."""
        token = "tok"
        buffer = (
            b"if [ -z \"${DOKLI_tok:-}\" ]; then DOKLI_tok=1; printf '\\n__DOKLI_START_tok\\n'; true; fi\r\n"
            b"\x1b[31mAuthentication failed: Please run ssh-add\x1b[0m\r\n"
            b"\x1b]0;window title\x07second remote line\r\n"
            b"__DOKLI_START_tok\r\n"
        )
        out = _partial_output(buffer, token)
        assert "Authentication failed: Please run ssh-add" in out
        assert "second remote line" in out
        assert token not in out
        assert "\x1b[" not in out
        assert "\x1b]" not in out
        assert "\r" not in out

    def test_empty_buffer_is_empty(self):
        """We expect no output when nothing was received."""
        assert _partial_output(b"", "tok") == ""
