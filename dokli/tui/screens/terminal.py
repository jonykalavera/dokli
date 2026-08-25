r"""Terminal screen: runs ``dokli terminal`` on a pty with keyboard passthrough.

The terminal CLI owns the interactive session (WebSocket to Dokploy, raw TTY,
exit detection); this screen spawns it on a pty, forwards every keystroke to
the pty master, and renders the ANSI stream through a real terminal emulator
(``pyte``) so backspace, cursor movement and the cursor position are correct —
unlike a naive ``Text.from_ansi``, which does not interpret ``\b`` or CSI
cursor sequences.
"""

import asyncio
import codecs
import contextlib
import fcntl
import os
import pty
import select
import struct
import subprocess
import sys
import termios
from typing import TYPE_CHECKING

import pyte
from rich.text import Text
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer, Header, Label, Static

from dokli.config import ConnectionConfig
from dokli.terminal_cli import DEFAULT_COLS, DEFAULT_ROWS

if TYPE_CHECKING:
    from textual.app import ComposeResult

#: Textual key -> terminal byte sequence for keys whose ``event.character`` is
#: None (navigation, function keys). Backspace is DEL (``\x7f``) — bash's erase
#: char — not the literal ``\x08`` Textual reports.
_KEY_SEQUENCES: dict[str, bytes] = {
    "backspace": b"\x7f",
    "enter": b"\r",
    "tab": b"\t",
    "up": b"\x1b[A",
    "down": b"\x1b[B",
    "right": b"\x1b[C",
    "left": b"\x1b[D",
    "home": b"\x1b[H",
    "end": b"\x1b[F",
    "pageup": b"\x1b[5~",
    "pagedown": b"\x1b[6~",
    "insert": b"\x1b[2~",
    "delete": b"\x1b[3~",
    "f1": b"\x1bOP",
    "f2": b"\x1bOQ",
    "f3": b"\x1bOR",
    "f4": b"\x1bOS",
    "f5": b"\x1b[15~",
    "f6": b"\x1b[17~",
    "f7": b"\x1b[18~",
    "f8": b"\x1b[19~",
    "f9": b"\x1b[20~",
    "f10": b"\x1b[21~",
    "f11": b"\x1b[23~",
    "f12": b"\x1b[24~",
}


def _key_to_bytes(event) -> bytes | None:
    r"""The terminal bytes for a Textual key event.

    Prefers ``event.character`` (printable/control chars); keys without one
    (navigation, function keys) use the escape-sequence mapping. ``ctrl+``
    chords map to their control byte (``ctrl+c`` -> ``\x03``).
    """
    if event.character:
        return event.character.encode("utf-8")
    key = event.key
    if key in _KEY_SEQUENCES:
        return _KEY_SEQUENCES[key]
    if key.startswith("ctrl+") and len(key) == 6:
        letter = key[5]
        if letter.isalpha():
            return bytes([ord(letter.lower()) - 96])
    return None


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
        self._screen: pyte.Screen | None = None
        self._emulator: pyte.Stream | None = None
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
            self._init_emulator()
            for frame in self._frames:
                self._feed(frame)
                self._paint()
                await asyncio.sleep(0.02)
            return
        argv = [sys.executable, "-m", "dokli", *terminal_argv(self.connection.name, self.container_id)]
        width = self._terminal_width()
        await asyncio.to_thread(self._spawn_pty, argv, width)
        # The CLI exited (e.g. the user typed `exit` and the session ended).
        # Leave the terminal screen and return to the browser.
        with contextlib.suppress(Exception):
            self.app.pop_screen()

    def _init_emulator(self, columns: int = 80, lines: int = 24) -> None:
        """(Re)create the pyte terminal emulator at the given size."""
        self._screen = pyte.Screen(columns, lines)
        self._emulator = pyte.Stream(self._screen)

    def _feed(self, text: str) -> None:
        """Feed a chunk of terminal output into the emulator."""
        if self._emulator is not None:
            self._emulator.feed(text)

    def _spawn_pty(self, argv: list[str], width: int) -> None:
        """Spawn ``dokli terminal`` on a pty and render its output.

        Blocks until the child exits; each chunk feeds the emulator and
        refreshes the frame through the event loop via ``call_from_thread``.
        """
        master, slave = pty.openpty()
        self._master = master
        rows = max(10, self.size.height or 24)
        columns = max(20, width)
        self.set_winsize(master, rows, columns)
        self._init_emulator(columns, rows)
        decoder = codecs.getincrementaldecoder("utf-8")(errors="replace")
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
                self._feed(decoder.decode(chunk))
                self.app.call_from_thread(self._paint)
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
        do not reach here. Navigation/function keys map to their terminal
        escape sequences so backspace, arrows, and Enter reach the shell.
        """
        if self._master is None:
            return
        data = _key_to_bytes(event)
        if not data:
            return
        with contextlib.suppress(OSError):
            os.write(self._master, data)
        event.stop()

    def _paint(self) -> None:
        """Render the emulator's screen state into the output widget."""
        if self._screen is None:
            return
        cy = self._screen.cursor.y
        cx = self._screen.cursor.x
        lines = list(self._screen.display)
        # Drop fully-empty trailing lines (the emulator pads to its height).
        while lines and not lines[-1].strip():
            lines.pop()
        text = Text()
        for row, line in enumerate(lines):
            if row > 0:
                text.append("\n")
            if row == cy:
                # Render the cursor row without stripping its trailing spaces:
                # the shell prompt ends in a space, and the cursor sits on that
                # cell, so rstrip would glue the cursor block to the prompt and
                # shift it while editing.
                text.append(line[:cx])
                if cx < len(line) and line[cx] != " ":
                    text.append(line[cx], style="reverse")
                    text.append(line[cx + 1 :])
                else:
                    text.append(" ", style="reverse")
                    text.append(line[cx + 1 :])
            else:
                text.append(line.rstrip())
        self.query_one("#terminal-output", Static).update(text)  # type: ignore[attr-defined]

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
