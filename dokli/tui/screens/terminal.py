"""Terminal screen: runs ``dokli terminal`` on a pty with keyboard passthrough.

The terminal CLI owns the interactive session (WebSocket to Dokploy, raw TTY,
exit detection); this screen spawns it on a pty, forwards every keystroke to
the pty master, and re-renders the ANSI output. This is the stats screen's
pty+stream pipeline made bidirectional.
"""

import asyncio
import codecs
import contextlib
import fcntl
import os
import pty
import re
import select
import struct
import subprocess
import sys
import termios
from typing import TYPE_CHECKING

from rich.text import Text
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer, Header, Label, Static

from dokli.config import ConnectionConfig
from dokli.terminal_cli import DEFAULT_COLS, DEFAULT_ROWS

if TYPE_CHECKING:
    from textual.app import ComposeResult

#: An incomplete escape tail dangling at the end of a chunk (see stats).
_ESCAPE_TAIL = re.compile(r"\x1b(?:\[[0-?]*[ -/]*)?$")


def clean_frame(stream: str) -> str:
    """The terminal frame with any cut-off escape sequence removed."""
    return _ESCAPE_TAIL.sub("", stream)


def terminal_argv(connection_name: str, container_id: str) -> list[str]:
    """CLI args for ``dokli terminal`` targeting a container."""
    return ["terminal", connection_name, "--container-id", container_id]


def terminal_command_hint(connection_name: str, container_id: str) -> str:
    """The exact ``dokli terminal ...`` command, as a hint line."""
    return "dokli " + " ".join(terminal_argv(connection_name, container_id))


class TerminalScreen(Screen):
    """An interactive shell into a container, run through a pty.

    ``container_id`` is the Docker container id/name. Keystrokes are forwarded
    to the pty (which the terminal CLI bridges to the Dokploy WebSocket), and
    the ANSI output is re-rendered live.
    """

    CSS = """
    #terminal-hint { padding: 0 1; color: $text-muted; }
    #terminal-scroll { height: 1fr; overflow-x: auto; scrollbar-gutter: stable; }
    #terminal-output { padding: 0 1; }
    """

    BINDINGS = [
        Binding("escape", "dismiss_screen", "Close"),
        Binding("q", "dismiss_screen", "Close"),
    ]

    def __init__(
        self,
        connection: ConnectionConfig,
        container_id: str,
        frames: list[str] | None = None,
        *args,
        **kwargs,
    ) -> None:
        """Construct the terminal screen.

        ``frames`` is a test hook: when provided, the screen replays those
        ANSI frames instead of spawning the on-disk CLI.
        """
        super().__init__(*args, **kwargs)
        self.connection = connection
        self.container_id = container_id
        self._frames = frames
        self._buffer = ""
        self._decoder = codecs.getincrementaldecoder("utf-8")(errors="replace")
        self._master: int | None = None
        self._process: subprocess.Popen | None = None

    def compose(self) -> "ComposeResult":
        """Compose the screen."""
        yield Header()
        yield Footer()
        yield Label(terminal_command_hint(self.connection.name, self.container_id), id="terminal-hint")
        yield VerticalScroll(Static("", id="terminal-output"), id="terminal-scroll")

    async def on_mount(self) -> None:
        """On mount, start the terminal."""
        self.sub_title = f"{self.connection.name} · terminal ({self.container_id})"
        self.run_worker(self._stream(), group="terminal")  # type: ignore[arg-type]

    async def _stream(self) -> None:
        """Run the CLI (or replay injected frames) and render each frame."""
        if self._frames is not None:
            for frame in self._frames:
                self._paint(frame)
                await asyncio.sleep(0.02)
            return
        argv = [sys.executable, "-m", "dokli", *terminal_argv(self.connection.name, self.container_id)]
        width = self._terminal_width()
        await asyncio.to_thread(self._spawn_pty, argv, width)

    def _spawn_pty(self, argv: list[str], width: int) -> None:
        """Spawn ``dokli terminal`` on a pty and render its output.

        Blocks until the child exits; each chunk refreshes the frame through
        the event loop via ``call_from_thread``.
        """
        master, slave = pty.openpty()
        self._master = master
        self.set_winsize(master, max(10, self.size.height or 24), max(20, width))
        self._buffer = ""
        self._decoder = codecs.getincrementaldecoder("utf-8")(errors="replace")
        try:
            process = subprocess.Popen(
                argv,
                stdin=slave,
                stdout=slave,
                stderr=slave,
                close_fds=True,
                start_new_session=True,
            )
        finally:
            os.close(slave)
        self._process = process
        try:
            while process.poll() is None:
                ready, _, _ = select.select([master], [], [], 0.2)
                if master not in ready:
                    continue
                try:
                    chunk = os.read(master, 65536)
                except OSError:
                    break
                if not chunk:
                    break
                self._buffer += self._decoder.decode(chunk)
                self.app.call_from_thread(self._paint, clean_frame(self._buffer))
        finally:
            if process.poll() is None:
                process.kill()
            os.close(master)
            self._master = None

    def _terminal_width(self) -> int:
        """The usable content width of the terminal output (main thread only)."""
        try:
            output = self.query_one("#terminal-output", Static)
            width = output.content_size.width
        except Exception:
            width = (self.size.width or 80) - 4
        return max(20, width)

    def _sync_pty_size(self) -> None:
        """Re-apply the current content size to the terminal pty on resize."""
        if self._master is None:
            return
        self.set_winsize(self._master, max(10, self.size.height or 24), self._terminal_width())

    @staticmethod
    def set_winsize(master: int, rows: int, columns: int) -> None:
        """Set the pty window size via ``TIOCSWINSZ``."""
        with contextlib.suppress(OSError):
            fcntl.ioctl(master, termios.TIOCSWINSZ, struct.pack("HHHH", rows, columns, 0, 0))

    def on_resize(self, event) -> None:
        """Reflow the terminal pty when the TUI terminal is resized."""
        self._sync_pty_size()

    def on_key(self, event) -> None:
        """Forward a keystroke to the terminal pty (keyboard passthrough).

        The bound close keys (escape/q) are handled by Textual's bindings and
        do not reach here. All other input is written to the pty master.
        """
        if self._master is None:
            return
        char = event.character
        if not char:
            return
        with contextlib.suppress(OSError):
            os.write(self._master, char.encode("utf-8"))
        event.stop()

    def _paint(self, frame: str) -> None:
        """Render the current frame (ANSI colors) into the output widget."""
        frame = frame.replace("\r", "")
        try:
            self.query_one("#terminal-output", Static).update(Text.from_ansi(frame))  # type: ignore[attr-defined]
        except Exception:
            return

    def action_dismiss_screen(self) -> None:
        """Close the terminal screen."""
        self.app.pop_screen()

    def on_screen_suspend(self, event) -> None:
        """Stop the terminal process when another screen is pushed on top."""
        process = self._process
        if process is not None and process.poll() is None:
            process.kill()

    def _kill_process(self) -> None:
        """Terminate the terminal subprocess if it is still running."""
        process = self._process
        if process is not None and process.poll() is None:
            process.kill()

    def on_mount_cleanup(self) -> None:
        """Ensure the terminal process is gone when the screen is removed."""
        self._kill_process()

    @staticmethod
    def _size_hint() -> tuple[int, int]:
        """The default pty size, matching the terminal CLI's fallback."""
        return DEFAULT_COLS, DEFAULT_ROWS
