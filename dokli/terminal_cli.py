"""The ``dokli terminal`` command: interactive shell into a container or host."""

import asyncio
import contextlib
import os
import re
import secrets
import signal
import sys
import termios
import tty
from collections.abc import Callable
from typing import Any

import typer
import websockets
from rich import print as rprint
from websockets.asyncio.client import ClientConnection

from dokli.config import Config, ConnectionConfig, complete_connection_names, resolve_connection
from dokli.errors import emit_error
from dokli.wss import CONTAINER_TERMINAL_ENDPOINT, HOST_TERMINAL_ENDPOINT, open_terminal, resize_message

#: Terminal size fallback when the window cannot be measured.
DEFAULT_COLS = 80
DEFAULT_ROWS = 24

#: Lines typed at the terminal that end the shell session (trailing spaces ok).
_EXIT_LINES = frozenset({b"exit", b"logout", b"quit", b"exit 0", b"exit 0;"})

#: Seconds between one-shot payload resends while waiting for the shell to
#: attach (Dokploy drops input sent before the exec/SSH channel is ready).
_RESEND_INTERVAL = 2.0

#: ANSI CSI escape sequence (used to clean partial terminal output).
_ANSI_CSI_RE = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")


def _is_exit_line(line: bytes) -> bool:
    r"""Whether a decoded input line ends the shell session.

    Ctrl+D (``\x04``) at the start of a line is the shell EOF. Word-exact
    ``exit``/``logout``/``quit`` (after stripping surrounding whitespace, so
    ``  exit  `` still matches) also end the session; anything else (e.g.
    ``echo exit``) does not.
    """
    stripped = line.strip(b" \t\r\n")
    if stripped.startswith(b"\x04"):
        return True
    return stripped in _EXIT_LINES


def build_command(config: Config) -> Callable[..., None]:
    """Return the ``terminal`` command function, bound to ``config``."""

    def terminal_command(
        connection_name: str | None = typer.Argument(
            None, help="Connection name.", shell_complete=complete_connection_names
        ),
        container_id: str = typer.Option(None, "--container-id", help="Docker container id or name."),
        server_id: str = typer.Option(None, "--server-id", help="Server id ('local' for the Dokploy host)."),
        active_way: str = typer.Option("sh", "--shell", help="Shell to run in the container (sh/bash/zsh/ash)."),
        service_id: str = typer.Option(None, "--service-id", help="Service id (authorization scope)."),
        username: str = typer.Option(None, "--username", help="SSH username (host terminal only)."),
        port: int = typer.Option(None, "--port", help="SSH port (host terminal only)."),
        command: str = typer.Option(
            None, "--command", help="Run a single command non-interactively and exit with its status."
        ),
    ) -> None:
        """Open an interactive shell into a container (or the host via SSH).

        Exactly one of --container-id or --server-id selects the target. For a
        host terminal, --username is required and --port defaults to 22. The
        terminal takes over the current TTY; exit with ``exit`` or Ctrl+D. With
        --command the command runs once, its output is printed, and dokli exits
        with the remote command's status, which may collide with dokli's own
        documented exit codes (1 runtime, 2 usage).
        """
        connection = resolve_connection(config, connection_name)
        if bool(container_id) == bool(server_id):
            raise typer.BadParameter("Provide exactly one of --container-id or --server-id.")
        if server_id and not username:
            raise typer.BadParameter("--username is required for a host terminal.")
        if command is not None:
            if not command.strip():
                raise typer.BadParameter("--command must not be empty.")
            code = asyncio.run(
                _run_one_shot(connection, container_id, server_id, active_way, service_id, username, port, command)
            )
            raise typer.Exit(code=code)
        asyncio.run(_run_terminal(connection, container_id, server_id, active_way, service_id, username, port))

    return terminal_command


def _endpoint_and_params(
    container_id: str | None,
    server_id: str | None,
    active_way: str,
    service_id: str | None,
    username: str | None,
    port: int | None,
) -> tuple[str, dict[str, Any]]:
    """Select the terminal endpoint and its query params for the target."""
    if container_id:
        return CONTAINER_TERMINAL_ENDPOINT, {
            "containerId": container_id,
            "activeWay": active_way,
            **({"serviceId": service_id} if service_id else {}),
        }
    return HOST_TERMINAL_ENDPOINT, {
        "serverId": server_id,
        "username": username,
        "port": port or 22,
    }


async def _run_terminal(
    connection: ConnectionConfig,
    container_id: str | None,
    server_id: str | None,
    active_way: str,
    service_id: str | None,
    username: str | None,
    port: int | None,
) -> None:
    """Stream the interactive terminal, bridging stdin/stdout to the socket."""
    endpoint, params = _endpoint_and_params(container_id, server_id, active_way, service_id, username, port)
    cols, rows = _terminal_size()
    params["cols"] = cols
    params["rows"] = rows
    try:
        ws = await open_terminal(connection, endpoint, params)
    except Exception as err:  # noqa: BLE001 - handshake/reachability failures.
        emit_error(f"Terminal connection failed: {err}")
    if sys.stdin.isatty():
        # Dokploy does not close the WebSocket when the shell exits (local
        # container path), so tell the user how to leave before the raw TTY
        # takes over and this line would be invisible.
        rprint(
            "[red]Note: Dokploy does not close this session on its own; type `exit` or Ctrl+D to leave.[/red]",
            file=sys.stderr,
        )
    try:
        await _bridge(ws)
    except Exception as err:  # noqa: BLE001 - the stream loop exits on any error.
        emit_error(f"Terminal failed: {err}")


async def _run_one_shot(
    connection: ConnectionConfig,
    container_id: str | None,
    server_id: str | None,
    active_way: str,
    service_id: str | None,
    username: str | None,
    port: int | None,
    command: str,
) -> int:
    """Run a single command over the terminal socket and return its exit code."""
    endpoint, params = _endpoint_and_params(container_id, server_id, active_way, service_id, username, port)
    try:
        ws = await open_terminal(connection, endpoint, params)
    except Exception as err:  # noqa: BLE001 - handshake/reachability failures.
        emit_error(f"Terminal connection failed: {err}")
    return await _run_remote_command(ws, command)


async def _run_remote_command(ws: ClientConnection, command: str, timeout: float = 60.0) -> int:
    """Run ``command`` over an open terminal socket and return its exit code.

    The Dokploy terminal is a raw PTY with no exit-code channel, so a sentinel
    pair of shell ``printf`` calls wraps the command: the exit status is echoed
    between full-line markers and parsed out of the PTY stream. The container
    endpoint never closes on shell exit, so the socket is force-closed.
    """
    token = secrets.token_hex(6)
    start = f"__DOKLI_START_{token}__"
    end = f"__DOKLI_EXIT_{token}__"
    # A guard variable makes the payload idempotent: Dokploy drops input sent
    # before the exec/SSH channel is attached, so we resend until the shell
    # accepts it, and only the first accepted copy runs the command. The
    # command also runs in a subshell so exit/return/exec cannot end the shell
    # before the trailing exit-marker printf runs.
    guard = f"DOKLI_{token}"
    payload = (
        f'if [ -z "${{{guard}:-}}" ]; then {guard}=1; '
        f"printf '\\n{start}\\n'; ( {command} ) 2>&1; "
        f"printf '\\n{end}:%s\\n' \"$?\"; fi\n"
    )
    await ws.send(payload.encode())
    buffer = b""
    loop = asyncio.get_running_loop()
    deadline = loop.time() + timeout
    parsed: tuple[str, int] | None = None
    try:
        # ponytail: buffers the full output and re-parses it per chunk; switch to
        # streaming/tail-parsing if large log output ever needs supporting here.
        while parsed is None:
            remaining = deadline - loop.time()
            if remaining <= 0:
                _write_partial(buffer, token)
                emit_error(f"Timed out after {timeout:.0f}s waiting for the remote command to finish.")
            try:
                chunk = await asyncio.wait_for(ws.recv(), timeout=min(_RESEND_INTERVAL, remaining))
            except asyncio.TimeoutError:
                await ws.send(payload.encode())
                continue
            except websockets.exceptions.ConnectionClosed:
                parsed = _parse_command_result(buffer, start, end)
                if parsed is None:
                    _write_partial(buffer, token)
                    emit_error("Terminal connection closed before the remote command finished.")
                break
            buffer += chunk if isinstance(chunk, bytes) else chunk.encode("utf-8")
            parsed = _parse_command_result(buffer, start, end)
        output, code = parsed
        if output and not output.endswith("\n"):
            output += "\n"
        sys.stdout.write(output)
        sys.stdout.flush()
        return code
    finally:
        # Always close: the container endpoint never closes on shell exit, and
        # every failure path (timeout, early close) must release the socket too.
        _close_socket(ws)


def _parse_command_result(buffer: bytes, start: str, end: str) -> tuple[str, int] | None:
    r"""Parse sentinel-wrapped command output from a PTY byte buffer.

    Full-line matching ignores the echoed input line (which contains the marker
    literals but never as a standalone line). Returns ``(output, exit_code)``
    with CRLF/CR normalized to ``\n`` and trailing newlines stripped, or
    ``None`` when the end marker has not arrived yet.
    """
    text = buffer.decode("utf-8", errors="replace")
    lines = re.split(r"\r\n|\r|\n", text)
    # A wrapped echoed input line can place the start marker on its own line
    # before the real one; the real marker is the last standalone occurrence.
    begin = max((index for index, line in enumerate(lines) if line == start), default=-1)
    if begin < 0:
        return None
    end_re = re.compile(rf"^{re.escape(end)}:(\d+)$")
    for index in range(begin + 1, len(lines)):
        match = end_re.match(lines[index])
        if match:
            output = "\n".join(lines[begin + 1 : index]).rstrip("\n")
            return output, int(match.group(1))
    return None


def _partial_output(buffer: bytes, token: str) -> str:
    """Best-effort remote output received before a failure.

    Strips the echoed payload and sentinel lines (any line containing the
    token), ANSI escapes, and CRLF/CR line endings so a useful remote message
    (e.g. an SSH auth failure) survives even when the end marker never arrives.
    """
    text = buffer.decode("utf-8", errors="replace").replace("\r\n", "\n").replace("\r", "\n")
    text = _ANSI_CSI_RE.sub("", text)
    lines = [line for line in text.split("\n") if token not in line]
    return "\n".join(lines).rstrip()


def _write_partial(buffer: bytes, token: str) -> None:
    """Write any partial remote output to stdout before reporting a failure."""
    partial = _partial_output(buffer, token)
    if partial:
        sys.stdout.write(partial + "\n")
        sys.stdout.flush()


async def _bridge(ws: ClientConnection) -> None:
    """Bidirectional bridge: stdin -> socket, socket -> stdout.

    The current TTY is put in raw mode so keystrokes pass through untouched;
    SIGWINCH sends a resize control message to the server. Ends when the
    socket closes (the server ended the session) or stdin reaches EOF.
    """
    loop = asyncio.get_running_loop()
    stdin = sys.stdin
    if stdin.isatty():
        fd = stdin.fileno()
        old = termios.tcgetattr(fd)
        tty.setraw(fd)
        try:
            loop.add_signal_handler(signal.SIGWINCH, lambda: _send_resize(ws))
            await _relay(ws)
        finally:
            loop.remove_signal_handler(signal.SIGWINCH)
            termios.tcsetattr(fd, termios.TCSADRAIN, old)
    else:
        await _relay(ws)


async def _relay(ws: ClientConnection) -> None:
    """Relay stdin -> socket and socket -> stdout, ending when either side ends.

    Whichever direction ends first (stdin EOF, an exit line closing the socket,
    or the server ending the session) cancels the other so the bridge returns.
    """
    stdin_task = asyncio.create_task(_read_stdin(ws))
    socket_task = asyncio.create_task(_read_socket(ws))
    done, pending = await asyncio.wait({stdin_task, socket_task}, return_when=asyncio.FIRST_COMPLETED)
    for task in pending:
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task
    for task in done:
        with contextlib.suppress(Exception):  # noqa: BLE001 - surface later if needed.
            task.result()


async def _read_stdin(ws: ClientConnection) -> None:
    """Forward raw stdin bytes to the socket, closing when an exit line is typed.

    Dokploy does not close the WebSocket when a container shell exits (local
    path), so when the user types an ``exit``/``logout``/``quit``/Ctrl+D line the
    socket is force-closed (via the transport) to end the session. For a
    container exec there is no outer shell, so this is the whole session; the
    host-SSH endpoint closes itself, making this a harmless fallback there.
    """
    loop = asyncio.get_running_loop()
    line = b""
    while True:
        data = await loop.run_in_executor(None, os.read, sys.stdin.fileno(), 4096)
        if not data:
            break
        await ws.send(data)
        # The pty echoes input back, so an exit line arrives twice: once raw
        # from the user and once echoed. Only act on the raw occurrence.
        line += data
        if b"\r" in line or b"\n" in line:
            head, _, rest = line.partition(b"\n")
            head = head.partition(b"\r")[0]
            if _is_exit_line(head):
                _close_socket(ws)
                return
            line = rest


async def _read_socket(ws: ClientConnection) -> None:
    """Forward socket output to stdout and exit cleanly when it closes."""
    try:
        async for chunk in ws:
            data = chunk if isinstance(chunk, bytes) else chunk.encode("utf-8")
            _write_stdout(data)
    except websockets.exceptions.ConnectionClosed:
        # The transport was force-closed (e.g. after an exit line) or the
        # server ended the session: this is the normal end of the terminal.
        pass


def _write_stdout(data: bytes) -> None:
    """Write terminal output to stdout (helper so tests can capture it)."""
    sys.stdout.buffer.write(data)
    sys.stdout.buffer.flush()


def _close_socket(ws: ClientConnection) -> None:
    """Force-close the terminal socket without waiting for a close handshake.

    Dokploy does not reply to WebSocket close frames on the container-terminal
    endpoint (local path), so ``await ws.close()`` would hang. Closing the
    underlying asyncio transport terminates the connection immediately.
    """
    transport = getattr(ws, "transport", None)
    if transport is not None:
        transport.close()
    else:
        asyncio.ensure_future(ws.close())  # pragma: no cover - defensive fallback


def _send_resize(ws: ClientConnection) -> None:
    """Send the current terminal size as a resize control message."""
    cols, rows = _terminal_size()
    loop = asyncio.get_event_loop()
    loop.create_task(ws.send(resize_message(cols, rows)))


def _terminal_size() -> tuple[int, int]:
    """The current terminal size (``(cols, rows)``), with a sane fallback."""
    try:
        import fcntl
        import struct

        with contextlib.suppress(OSError):
            packed = fcntl.ioctl(sys.stdout.fileno(), termios.TIOCGWINSZ, b"\x00" * 8)
            rows, cols, _, _ = struct.unpack("HHHH", packed)
            if cols > 0 and rows > 0:
                return cols, rows
    except Exception:  # noqa: BLE001 - fall back to defaults on any error.
        pass
    return DEFAULT_COLS, DEFAULT_ROWS
