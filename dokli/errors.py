"""Stable error channel: consistent exit codes and machine-readable errors.

Exit codes are part of dokli's contract for scripting/agents:

- ``0`` success
- ``1`` runtime/API error
- ``2`` usage error (bad/unknown arguments)

When a command requested a machine format (``--format json`` or ``agent``),
errors are emitted to stderr as a JSON object ``{"error": ..., "exit_code": N}``
instead of rich text, so callers can parse failures reliably.
"""

import json
import sys
from typing import NoReturn

import typer
from rich import print as rprint

from dokli.formatting import Format

EXIT_OK = 0
EXIT_ERROR = 1
EXIT_USAGE = 2


def emit_error(message: str, format: Format | None = None, exit_code: int = EXIT_ERROR) -> NoReturn:
    """Write an error to stderr and exit with ``exit_code``.

    Under ``--format json``/``agent`` the message is a JSON object on stderr;
    otherwise a rich red line. Always exits (never returns).
    """
    if format in (Format.json, Format.agent):
        print(json.dumps({"error": message, "exit_code": exit_code}), file=sys.stderr)  # noqa: T201
    else:
        rprint(f"[red]{message}[/red]", file=sys.stderr)
    raise typer.Exit(code=exit_code)


def format_from_argv(argv: list[str] | None = None) -> Format | None:
    """The machine ``--format`` value present in ``argv`` (used by the top-level entry).

    Errors at the entry point (before a command runs) don't have a command-local
    ``--format`` in scope, so we scan the raw argv to decide whether failures
    should be machine-readable. Returns ``None`` when no json/agent format is
    requested.
    """
    argv = argv if argv is not None else sys.argv[1:]
    for index, arg in enumerate(argv):
        if arg == "--format" and index + 1 < len(argv):
            try:
                candidate = Format(argv[index + 1])
            except ValueError:
                return None
            return candidate if candidate in (Format.json, Format.agent) else None
        if arg.startswith("--format="):
            try:
                candidate = Format(arg.split("=", 1)[1])
            except ValueError:
                return None
            return candidate if candidate in (Format.json, Format.agent) else None
    return None
