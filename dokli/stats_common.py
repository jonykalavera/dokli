"""Shared presentation helpers for the ``dokli stats`` CLI and TUI.

The CLI renders the live stats boxes; the TUI spawns that same CLI on a pty and
re-renders its ANSI stream (a preamble for the future container-terminal
socket). Everything both sides need to agree on lives here: the metric set,
palette, and how to build the ``dokli stats`` command line.
"""

from dataclasses import dataclass

#: Metric display order for the stats block.
METRICS = ("cpu", "memory", "network", "block", "disk")
#: Metrics rendered as a two-direction (down/up) mirrored sparkline.
DUO_METRICS = ("network", "block")
#: Per-metric label/graph colors, btop-like (Catppuccin **Mocha** palette, for
#: the dark theme).
METRIC_COLORS = {
    "cpu": "#89dceb",  # sky
    "memory": "#a6e3a1",  # green
    "network": "#f9e2af",  # yellow
    "block": "#cba6f7",  # mauve
    "disk": "#f38ba8",  # red
}
#: Rounded-box border color (Catppuccin Mocha overlay0, muted).
BORDER_COLOR = "#6c7086"

#: Per-metric colors for the light theme (Catppuccin Latte, saturated so the
#: pastel-dark variants stay usable on a light background).
_LIGHT_METRIC_COLORS = {
    "cpu": "#04a5e5",  # sky
    "memory": "#40a02b",  # green
    "network": "#df8e1d",  # yellow
    "block": "#8839ef",  # mauve
    "disk": "#d20f39",  # red
}
#: Rounded-box border color (Catppuccin Latte overlay0).
_LIGHT_BORDER_COLOR = "#6c6f85"


@dataclass(frozen=True)
class Palette:
    """The colors a stats render uses: per-metric colors plus the border."""

    metric_colors: dict[str, str]
    border_color: str


def palette_for(dark: bool) -> Palette:
    """The palette for a theme (``dark`` uses Mocha, light uses Latte)."""
    if dark:
        return Palette(METRIC_COLORS, BORDER_COLOR)
    return Palette(_LIGHT_METRIC_COLORS, _LIGHT_BORDER_COLOR)

#: Target kinds accepted by ``dokli stats --<kind>-id``, plus system.
TARGET_KINDS = ("system", "compose", "application", "container")


def blend_color(hex_color: str, amount: float, target: int) -> str:
    """Blend each ``#rrggbb`` channel toward ``target`` by ``amount`` (0..1)."""
    hex_color = hex_color.lstrip("#")
    channels = (int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
    return "#" + "".join(f"{round(c + (target - c) * amount):02x}" for c in channels)


def lighten_color(hex_color: str, amount: float = 0.35) -> str:
    """Blend a ``#rrggbb`` color toward white by ``amount``."""
    return blend_color(hex_color, amount, 255)


def darken_color(hex_color: str, amount: float = 0.35) -> str:
    """Blend a ``#rrggbb`` color toward black by ``amount``."""
    return blend_color(hex_color, amount, 0)


def metrics_for(display_type: str) -> tuple[str, ...]:
    """Metrics to show: disk is only reported for host system stats."""
    if display_type == "system":
        return METRICS
    return tuple(name for name in METRICS if name != "disk")


def default_samples(width: int) -> int:
    """Adaptive default history: enough samples to fill the console width."""
    return max(10, 2 * (width - 2))


def stats_argv(connection_name: str, kind: str, ident: str | None = None) -> list[str]:
    """CLI args for ``dokli stats`` targeting ``kind``.

    ``kind`` is one of :data:`TARGET_KINDS`; ``ident`` is the record id for
    compose/application/container targets. The returned list starts with the
    ``stats`` subcommand (prepend the executable to spawn it).
    """
    args = ["stats", connection_name]
    if kind == "compose":
        args += ["--compose-id", str(ident)]
    elif kind == "application":
        args += ["--application-id", str(ident)]
    elif kind == "container":
        args += ["--container-id", str(ident)]
    return args


def stats_command_hint(connection_name: str, kind: str, ident: str | None = None) -> str:
    """The exact ``dokli stats ...`` command for a target, as a hint line."""
    return "dokli " + " ".join(stats_argv(connection_name, kind, ident))