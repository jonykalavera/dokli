"""The ``dokli stats`` command: live container stats over WebSocket."""

import asyncio
import json
import os
import shutil
import sys
from collections import deque
from collections.abc import Callable
from datetime import datetime

import httpx
import typer
import websockets
from rich import print as rprint
from rich.console import Console

from dokli.api_client import request_json
from dokli.config import Config, complete_connection_names, resolve_connection
from dokli.formatting import Format
from dokli.monitoring import (
    METRIC_SCALE,
    format_duo_total_label,
    metric_duo,
    metric_value,
    metric_value_text,
    render_dual_sparkline,
    render_sparkline,
)
from dokli.stats_common import (
    DUO_METRICS,
    METRICS,
    darken_color,
    default_samples,
    lighten_color,
    metrics_for,
    palette_for,
)
from dokli.wss import iter_stats

# Module-level aliases so the CLI reads like before.
_DUO_METRICS = DUO_METRICS
_METRICS = METRICS
_lighten_color = lighten_color
_darken_color = darken_color
_default_samples = default_samples
_metrics_for = metrics_for
#: Color console with rich's number highlighter disabled (labels are raw).
_console = Console(highlight=False)


def resolve_palette() -> tuple[dict[str, str], str]:
    """The ``(metric_colors, border)`` for the active theme.

    ``DOKLI_THEME=light`` selects the Catppuccin Latte palette (used by the TUI
    in light mode); anything else defaults to the dark Mocha palette.
    """
    dark = os.environ.get("DOKLI_THEME", "dark") != "light"
    palette = palette_for(dark)
    return palette.metric_colors, palette.border_color


def build_command(config: Config) -> Callable[..., None]:
    """Return the ``stats`` command function, bound to ``config``."""

    def stats_command(
        connection_name: str | None = typer.Argument(
            None, help="Connection name.", shell_complete=complete_connection_names
        ),
        compose_id: str = typer.Option(None, "--compose-id", help="Compose service id."),
        application_id: str = typer.Option(None, "--application-id", help="Application service id."),
        container_name: str = typer.Option(None, "--container-name", help="Docker container name."),
        container_id: str = typer.Option(None, "--container-id", help="Docker container id."),
        app_name: str = typer.Option(None, "--app-name", help="Raw stats appName (default: dokploy = system)."),
        app_type: str = typer.Option(None, "--app-type", help="Raw stats appType (application|stack|docker-compose)."),
        height: int = typer.Option(3, "--height", help="Sparkline height in rows (1-8)."),
        samples: int = typer.Option(None, "--samples", help="History samples (default: console width)."),
        no_backfill: bool = typer.Option(False, "--no-backfill", help="Skip the REST history backfill (system-only)."),
        once: bool = typer.Option(False, "--once", help="Print a single snapshot and exit (no live stream)."),
        format: Format = typer.Option(  # noqa: B008
            Format.python, "--format", help="Output format (python = braille; agent = NDJSON dataframe)."
        ),
    ) -> None:
        """Stream a service's or the host system's stats live (Ctrl+C to stop)."""
        connection = resolve_connection(config, connection_name)
        selectors = (compose_id, application_id, container_name, container_id)
        if sum(bool(x) for x in selectors) > 1:
            raise typer.BadParameter(
                "Provide at most one of --compose-id, --application-id, --container-name, --container-id."
            )
        if any(selectors) and (app_name or app_type):
            raise typer.BadParameter("--app-name/--app-type cannot be combined with a service selector.")
        if app_type and app_type not in ("application", "stack", "docker-compose"):
            raise typer.BadParameter("--app-type must be one of: application, stack, docker-compose.")
        if not 1 <= height <= 8:
            raise typer.BadParameter("--height must be between 1 and 8.")
        if samples is not None and samples < 1:
            raise typer.BadParameter("--samples must be at least 1.")
        if samples is None:
            samples = _default_samples(shutil.get_terminal_size((80, 24)).columns)
        asyncio.run(
            _stream_stats(
                connection,
                compose_id,
                application_id,
                container_name,
                container_id,
                app_name,
                app_type,
                height,
                samples,
                no_backfill,
                once,
                format,
            )
        )

    return stats_command


async def _stream_stats(
    connection,
    compose_id: str | None,
    application_id: str | None,
    container_name: str | None,
    container_id: str | None,
    app_name: str | None,
    app_type: str | None,
    height: int,
    samples: int,
    no_backfill: bool,
    once: bool,
    format: Format = Format.python,
) -> None:
    """Stream and print a service's or the host system's stats as braille sparklines.

    With ``format=agent`` it instead emits an NDJSON dataframe (header row once,
    then one row per sample) — machine-friendly, low footprint.
    """
    app_name, app_type, display_type, project_name, service_label = await _resolve_stats_target(
        connection, compose_id, application_id, container_name, container_id, app_name, app_type
    )
    if format == Format.agent:
        await _stream_agent(connection, app_name, app_type, display_type, once)
        return
    metrics = _metrics_for(display_type)
    buffers: dict[str, deque[float]] = {}
    duo_buffers: dict[str, tuple[deque[float], deque[float]]] = {
        name: (deque(maxlen=samples), deque(maxlen=samples)) for name in _DUO_METRICS
    }
    # Parallel, lockstep timestamps (ISO) so the header can show the order window
    # actually visible in the charts.
    timestamps: dict[str, deque[str]] = {name: deque(maxlen=samples) for name in metrics}
    live = sys.stdout.isatty() and not once
    block_lines = 0
    if live:
        # The monitor owns the whole screen: clear it before the first block so
        # the redraw never scrolls past stale content.
        sys.stdout.write("\033[2J\033[H")
        sys.stdout.flush()
    base_header = _format_header(connection.name, project_name, service_label, display_type)
    if not no_backfill:
        # Prime the charts with the REST history (web parity) so the first frame
        # is already full. Never block startup: degrade to live-only on failure.
        if live:
            block_lines = _print_loading(base_header, metrics, height)
            sys.stdout.flush()
        history = await asyncio.to_thread(_fetch_history_stats, connection, app_name)
        _fill_from_history(history, buffers, duo_buffers, timestamps, metrics, samples)
    if live and block_lines:
        _clear_lines(block_lines)
    block_lines = 0
    try:
        async for data in iter_stats(connection, app_name, app_type):
            if live and block_lines:
                _clear_lines(block_lines)
            block_lines = _print_block(base_header, data, buffers, duo_buffers, metrics, height, timestamps)
            sys.stdout.flush()
            if once:
                break
    except KeyboardInterrupt:
        pass
    except websockets.exceptions.ConnectionClosed:
        pass
    except (websockets.exceptions.WebSocketException, OSError) as err:
        rprint(f"[red]Stats stream failed: {err}[/red]")
        raise typer.Exit(code=1) from None


#: Column names for the ``--format agent`` stats dataframe (flat, __-joined).
_AGENT_COLUMNS = [
    "time",
    "cpu",
    "memory",
    "network__down",
    "network__up",
    "block__down",
    "block__up",
    "disk",
]


async def _stream_agent(connection, app_name: str, app_type: str, display_type: str, once: bool) -> None:
    """Emit an NDJSON stats dataframe: header once, then one row per sample."""
    print(json.dumps(_AGENT_COLUMNS))  # noqa: T201
    try:
        async for data in iter_stats(connection, app_name, app_type):
            row = [_agent_row(data, display_type)]
            print(json.dumps(row[0]), flush=True)  # noqa: T201
            if once:
                break
    except KeyboardInterrupt:
        pass
    except websockets.exceptions.ConnectionClosed:
        pass
    except (websockets.exceptions.WebSocketException, OSError) as err:
        rprint(f"[red]Stats stream failed: {err}[/red]", file=sys.stderr)
        raise typer.Exit(code=1) from None


def _agent_row(data: dict, display_type: str) -> list:
    """One dataframe row for a stats sample (positional, in _AGENT_COLUMNS order)."""
    entry = data.get("cpu") or {}
    cpu = metric_value({"cpu": entry}, "cpu")
    memory = metric_value(data, "memory")
    network = metric_duo(data, "network")
    block = metric_duo(data, "block")
    disk = metric_value(data, "disk") if display_type == "system" else None
    timestamp = (data.get("cpu") or {}).get("time")
    return [
        timestamp,
        cpu,
        memory,
        network[0] if network else None,
        network[1] if network else None,
        block[0] if block else None,
        block[1] if block else None,
        disk,
    ]


async def _resolve_stats_target(
    connection, compose_id, application_id, container_name, container_id, app_name, app_type
):
    """Resolve the stats WebSocket ``(appName, appType)`` from a selector.

    Also returns the display type, project and service label for the header.
    Compose/application stats use the service's appName; a bare container is
    targeted by its docker name (the stats endpoint filters compose containers
    by docker name, so ``appType=docker-compose`` matches any container). With
    no selector the raw ``appName``/``appType`` are used, defaulting to
    ``dokploy``/``application`` which returns the host system stats.
    """
    if compose_id:
        compose = await asyncio.to_thread(request_json, connection, "compose.one", {"composeId": compose_id})
        app_name = compose.get("appName")
        if not app_name:
            raise typer.BadParameter("Compose has no appName.")
        app_type = compose.get("composeType") or "docker-compose"
        project_name = ((compose.get("environment") or {}).get("project") or {}).get("name")
        return app_name, app_type, app_type, project_name, app_name

    if application_id:
        application = await asyncio.to_thread(
            request_json, connection, "application.one", {"applicationId": application_id}
        )
        app_name = application.get("appName")
        if not app_name:
            raise typer.BadParameter("Application has no appName.")
        return app_name, "application", "application", None, application.get("name") or app_name

    if container_id:
        # Resolve the docker name by id (prefix match, like docker) so the
        # stats filter can target the exact container.
        containers = await asyncio.to_thread(request_json, connection, "docker.getContainers", {})
        matches = [c for c in containers if c.get("containerId", "").startswith(container_id)]
        if not matches:
            raise typer.BadParameter(f"No running container matches id {container_id!r}.")
        container_name = matches[0].get("name")
    if container_name:
        return container_name, "docker-compose", "container", None, container_name

    # No selector: raw appName/appType, defaulting to the host system stats.
    resolved_name = app_name or "dokploy"
    resolved_type = app_type or "application"
    display_type = "system" if resolved_name == "dokploy" else resolved_type
    return resolved_name, resolved_type, display_type, None, resolved_name


def _fetch_history_stats(connection, app_name: str) -> dict:
    """The stored stats history for ``app_name`` (web parity backfill).

    Returns ``{}`` on any failure or unexpected payload so startup never blocks.
    """
    try:
        history = request_json(connection, "application.readAppMonitoring", {"appName": app_name})
    except (httpx.HTTPError, OSError, ValueError):
        return {}
    return history if isinstance(history, dict) else {}


def _fill_from_history(history: dict, buffers, duo_buffers, timestamps, metrics, samples: int) -> None:
    """Prime the chart buffers (and their timestamps) from the REST history.

    History is oldest-first; appends in order so the newest sample lands at the
    right edge. A metric is skipped when its series is absent (e.g. disk for
    non-system targets).
    """
    for name in metrics:
        series = history.get(name) if isinstance(history, dict) else None
        if not isinstance(series, list) or not series:
            continue
        stamp = timestamps.setdefault(name, deque(maxlen=samples))
        if name in _DUO_METRICS:
            down_deque, up_deque = duo_buffers[name]
            for entry in series:
                if not isinstance(entry, dict):
                    continue
                duo = metric_duo({name: entry}, name)
                if duo is None:
                    continue
                down, up = duo
                down_deque.append(down)
                up_deque.append(up)
                stamp.append(entry.get("time", ""))
        elif isinstance(series[0], dict):
            buffer = buffers.setdefault(name, deque(maxlen=samples))
            for entry in series:
                sample_value = metric_value({name: entry}, name)
                if sample_value is not None:
                    buffer.append(sample_value)
                    stamp.append(entry.get("time", ""))


def _print_loading(header: str, metrics: tuple[str, ...], height: int) -> int:
    """Render a loading frame (TTY only) with one box per metric."""
    inner_width = max(10, shutil.get_terminal_size((80, 24)).columns - 2)
    metric_colors, border_color = resolve_palette()
    print(header)  # noqa: T201
    lines = 1
    for name in metrics:
        color = metric_colors[name]
        spark = "\n".join([""] * (2 * height if name in _DUO_METRICS else height))
        lines += _print_metric_box(name, "loading\u2026", spark, color, None, None, inner_width, border_color)
    return lines


def _format_header(
    connection: str, project: str | None, service: str, app_type: str, time_range: tuple[str, str] | None = None
) -> str:
    """The context line shown above the metrics (scope › service, app type)."""
    scope = f"{project}/{service}" if project else service
    header = f"{connection} \u203a {scope} ({app_type})"
    if time_range:
        header = _header_with_range(header, time_range)
    return header


def _format_time(value) -> str | None:
    """``HH:MM:SS`` (local) for an ISO-8601 timestamp, or ``None``."""
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00")).astimezone().strftime("%H:%M:%S")
    except (ValueError, TypeError):
        return None


def _header_with_range(header: str, time_range: tuple[str, str] | None) -> str:
    """The header with the sample time range, e.g. ``… · 13:32:04→13:38:12``.

    ``time_range`` is the ``(start, end)`` of the visible chart window.
    """
    if not time_range:
        return header
    start, end = time_range
    return f"{header} \u00b7 {start}\u2192{end}"


def _print_block(
    header: str,
    data: dict,
    buffers: dict[str, deque[float]],
    duo_buffers: dict[str, tuple[deque[float], deque[float]]],
    metrics: tuple[str, ...],
    height: int,
    timestamps: dict[str, deque[str]],
) -> int:
    """Print the header + one rounded metric box per metric, returning the line count."""
    inner_width = max(10, shutil.get_terminal_size((80, 24)).columns - 2)
    metric_colors, border_color = resolve_palette()
    print(_header_with_range(header, _visible_range(timestamps)))  # noqa: T201
    lines = 1
    for name in metrics:
        color = metric_colors[name]
        stamp_deque = timestamps.get(name)
        if name in _DUO_METRICS:
            down_deque, up_deque = duo_buffers[name]
            raw = metric_duo(data, name)
            if raw is not None:
                down, up = raw
                down_deque.append(down)
                up_deque.append(up)
                if stamp_deque is not None:
                    stamp_deque.append((data.get(name) or {}).get("time", ""))
            # Plot the raw cumulative counters (flat line when idle), matching
            # the web UI: network/block are cumulative totals, not rates.
            label = format_duo_total_label(*raw) if raw is not None else "-"
            spark = render_dual_sparkline(
                _wide(list(down_deque), 2 * inner_width),
                _wide(list(up_deque), 2 * inner_width),
                height=height,
            )
            light_color = _lighten_color(color)
            dark_color = _darken_color(color)
        else:
            value = metric_value(data, name)
            if value is not None:
                buffers.setdefault(name, deque(maxlen=2 * inner_width)).append(value)
                deque_for_ts = timestamps.setdefault(name, deque(maxlen=2 * inner_width))
                deque_for_ts.append((data.get(name) or {}).get("time", ""))
            label = metric_value_text(data, name)
            spark = render_sparkline(
                _wide(list(buffers.get(name, ())), 2 * inner_width),
                height=height,
                vmax=METRIC_SCALE[name],
            )
            light_color = None
            dark_color = None
        lines += _print_metric_box(name, label, spark, color, light_color, dark_color, inner_width, border_color)
    return lines


def _visible_range(timestamps: dict[str, deque[str]]) -> tuple[str, str] | None:
    """The ``(start, end)`` HH:MM:SS window actually shown in the charts.

    Spans the oldest to the newest timestamp across all metric series, all
    trimmed to the buffer size (so it scrolls forward as samples age out).
    """
    starts: list[str] = []
    ends: list[str] = []
    for stamp in timestamps.values():
        if not stamp:
            continue
        start = _format_time(stamp[0])
        end = _format_time(stamp[-1])
        if start:
            starts.append(start)
        if end:
            ends.append(end)
    if not starts or not ends:
        return None
    return min(starts), max(ends)


def _wide(values: list[float], width: int) -> list[float]:
    """Keep at most the newest ``width`` values (newest at the right edge)."""
    values = list(values)
    return values[-width:] if len(values) > width else values


def _print_metric_box(
    name: str,
    label: str,
    spark: str,
    color: str,
    light_color: str | None,
    dark_color: str | None,
    inner_width: int,
    border_color: str,
) -> int:
    """Print one rounded box: label in the top border, graph full-bleed below.

    For two-direction graphs (``light_color``/``dark_color`` set) the upper
    half renders lighter and the lower half darker so up/down dots stay clearly
    distinguishable. Returns the number of lines printed (top + graph + bottom).
    """
    border = border_color
    label_text = f"{name.upper()} {label}"
    fill = max(0, inner_width + 2 - len("╭─ ") - len(label_text) - len(" ╮"))
    _console.print(f"[{border}]╭─ [/][{color}]{label_text}[/][{border}] {'─' * fill}╮[/]", soft_wrap=True)
    rows = spark.split("\n") or [""]
    mid = len(rows) // 2
    for i, row in enumerate(rows):
        if light_color is not None and i < mid:
            col = light_color
        elif dark_color is not None and i >= mid:
            col = dark_color
        else:
            col = color
        content = row.replace("\u2800", " ").rjust(inner_width)
        if content.strip():
            _console.print(f"[{border}]│[/][{col}]{content}[/][{border}]│[/]", soft_wrap=True)
        else:
            _console.print(f"[{border}]│[/]{' ' * inner_width}[{border}]│[/]", soft_wrap=True)
    _console.print(f"[{border}]╰[/]{'─' * inner_width}[{border}]╯[/]", soft_wrap=True)
    return len(rows) + 2


def _clear_lines(count: int) -> None:
    """Move the cursor up and clear the previously printed block."""
    sys.stdout.write(f"\033[{count}A\033[J")
