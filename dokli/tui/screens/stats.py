"""Live stats screen: runs ``dokli stats`` on a pty and shows its ANSI frame.

The stats CLI owns the rendering (boxes, colors, redraw); this screen just
spawns it on a pty, captures the ANSI-clearing stream, and re-renders the
current frame. That pty+stream+render pipeline is the same shape the future
container-terminal socket will need, so this acts as its proof of concept.
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
from dokli.stats_common import stats_argv, stats_command_hint

if TYPE_CHECKING:
    from textual.app import ComposeResult

#: An incomplete escape tail (bare ``ESC``, or a CSI without its terminating
#: final byte) dangling at the end of a chunk. Rich's ``from_ansi`` drops
#: complete CSIs but renders an unfinished one as literal noise, so strip it.
_ESCAPE_TAIL = re.compile(r"\x1b(?:\[[0-?]*[ -/]*)?$")


def current_frame(stream: str) -> str:
    """The visible frame in an ANSI-clear redraw stream.

    Each CLI sample either clears the screen (``ESC[2J ESC[H``) at start or a
    redraw (``ESC[nA ESC[J``) before reprinting; the current frame is whatever
    follows the last such ``ESC[J``.
    """
    idx = stream.rfind("\x1b[J")
    if idx >= 0:
        return stream[idx + 3 :]
    start = stream.find("\x1b[2J\x1b[H")
    if start >= 0:
        return stream[start + 7 :]
    return stream


def clean_frame(stream: str) -> str:
    """The current frame with any cut-off escape sequence removed.

    A pty read can split an escape sequence mid-way; once the ES incomplete
    tail is trimmed, ``Text.from_ansi`` no longer leaks a stray ``ESC``/``[``
    into the render (the likely artifact behind the "noise" on the network and
    block charts inside the TUI).
    """
    return _ESCAPE_TAIL.sub("", current_frame(stream))


class StatsScreen(Screen):
    """Live stats for a system, service, or container.

    ``kind`` is one of ``system``/``compose``/``application``/``container``;
    ``ident`` is the record id for compose/application/container targets. The
    screen shows the exact ``dokli stats`` command (preamble) plus the live
    frame rendered from the CLI's pty stream.
    """

    CSS = """
    #stats-hint { padding: 0 1; color: $text-muted; }
    #stats-scroll { height: 1fr; }
    #stats-output { padding: 0 1; }
    """

    BINDINGS = [
        Binding("escape", "dismiss_screen", "Close"),
        Binding("q", "dismiss_screen", "Close"),
    ]

    def __init__(
        self,
        connection: ConnectionConfig,
        kind: str,
        ident: str | None = None,
        frames: list[str] | None = None,
        *args,
        **kwargs,
    ) -> None:
        """Construct the stats screen.

        ``frames`` is a test hook: when provided, the screen replays those
        ANSI frames instead of spawning the on-disk CLI.
        """
        super().__init__(*args, **kwargs)
        self.connection = connection
        self.kind = kind
        self.ident = ident
        self._frames = frames
        self._buffer = ""
        self._decoder = codecs.getincrementaldecoder("utf-8")(errors="replace")
        self._master: int | None = None
        self._restart = False
        self._process: subprocess.Popen | None = None

    def compose(self) -> "ComposeResult":
        """Compose the screen."""
        yield Header()
        yield Footer()
        yield Label(
            stats_command_hint(self.connection.name, self.kind, self.ident),
            id="stats-hint",
        )
        yield VerticalScroll(Static("", id="stats-output"), id="stats-scroll")

    async def on_mount(self) -> None:
        """On mount, start the stats stream."""
        self.sub_title = f"{self.connection.name} · stats ({self.kind})"
        self.run_worker(self._stream(), group="stats")  # type: ignore[arg-type]

    async def _stream(self) -> None:
        """Run the CLI (or replay injected frames) and render each frame."""
        if self._frames is not None:
            for frame in self._frames:
                self._paint(frame)
                await asyncio.sleep(0.02)
            return
        argv = [sys.executable, "-m", "dokli", *stats_argv(self.connection.name, self.kind, self.ident)]
        while True:
            self._buffer = ""
            await asyncio.to_thread(self._spawn_pty, argv)
            # Re-armed? The child exited because of a dark/light toggle.
            if not self._restart:
                break
            self._restart = False

    def theme_changed(self, dark: bool) -> None:
        """Re-render the stats with the new theme when dark mode toggles.

        ``dark`` is the app's new value; the running CLI is killed so the
        stream loop re-spawns it with the matching ``DOKLI_THEME``.
        """
        if self._process is not None and self._process.poll() is None:
            self._restart = True
            self._process.kill()

    @staticmethod
    def _spawn_env(dark: bool) -> dict:
        """The environment for the stats CLI, signaling the active theme."""
        return {**os.environ, "DOKLI_THEME": "dark" if dark else "light"}

    def _spawn_pty(self, argv: list[str]) -> None:
        """Spawn ``dokli stats`` on a pty and render its redraw stream.

        Blocks until the child exits; each chunk refreshes the frame through
        the event loop via ``call_from_thread``.
        """
        master, slave = pty.openpty()
        self._master = master
        self._sync_pty_size()
        self._buffer = ""
        self._decoder = codecs.getincrementaldecoder("utf-8")(errors="replace")
        env = StatsScreen._spawn_env(self.app.dark)
        try:
            process = subprocess.Popen(
                argv,
                stdin=subprocess.DEVNULL,
                stdout=slave,
                stderr=slave,
                close_fds=True,
                start_new_session=True,
                env=env,
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

    def _sync_pty_size(self) -> None:
        """Push the app's current size to the stats pty, so the CLI reflows."""
        if self._master is None:
            return
        width = max(20, (self.size.width or 80) - 2)
        self.set_winsize(self._master, max(10, self.size.height or 24), width)

    @staticmethod
    def set_winsize(master: int, rows: int, columns: int) -> None:
        """Set the pty window size via ``TIOCSWINSZ``."""
        with contextlib.suppress(OSError):
            fcntl.ioctl(master, termios.TIOCSWINSZ, struct.pack("HHHH", rows, columns, 0, 0))

    def on_resize(self, event) -> None:
        """Reflow the stats pty when the TUI terminal is resized."""
        self._sync_pty_size()

    def _paint(self, frame: str) -> None:
        """Render the current frame (ANSI colors) into the output widget."""
        frame = frame.replace("\r", "")
        try:
            self.query_one("#stats-output", Static).update(Text.from_ansi(frame))  # type: ignore[attr-defined]
        except Exception:
            return

    def action_dismiss_screen(self) -> None:
        """Close the stats screen."""
        self.app.pop_screen()

    def on_screen_suspend(self, event) -> None:
        """Stop the stats process when another screen is pushed on top."""
        process = self._process
        if process is not None and process.poll() is None:
            process.kill()

    def _kill_process(self) -> None:
        """Terminate the stats subprocess if it is still running."""
        process = self._process
        if process is not None and process.poll() is None:
            process.kill()

    def on_mount_cleanup(self) -> None:
        """Ensure the stats process is gone when the screen is removed."""
        self._kill_process()