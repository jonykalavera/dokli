"""The ``dokli terminal`` command: interactive shell into a container or host."""

import asyncio
import contextlib
import os
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
    ) -> None:
        """Open an interactive shell into a container (or the host via SSH).

        Exactly one of --container-id or --server-id selects the target. For a
        host terminal, --username is required and --port defaults to 22. The
        terminal takes over the current TTY; exit with ``exit`` or Ctrl+D.
        """
        connection = resolve_connection(config, connection_name)
        if bool(container_id) == bool(server_id):
            raise typer.BadParameter("Provide exactly one of --container-id or --server-id.")
        if server_id and not username:
            raise typer.BadParameter("--username is required for a host terminal.")
        asyncio.run(_run_terminal(connection, container_id, server_id, active_way, service_id, username, port))

    return terminal_command


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
    if container_id:
        params: dict[str, Any] = {
            "containerId": container_id,
            "activeWay": active_way,
            **({"serviceId": service_id} if service_id else {}),
        }
        endpoint = CONTAINER_TERMINAL_ENDPOINT
    else:
        params = {
            "serverId": server_id,
            "username": username,
            "port": port or 22,
        }
        endpoint = HOST_TERMINAL_ENDPOINT
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
