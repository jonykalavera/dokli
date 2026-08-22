"""Braille sparklines and metric extraction for live monitoring stats."""

import re

from braillegraph import horizontal_graph

#: Braille bar graphs render one row per 4 units of value.
_ROWS_PER_UNIT = 4


def _pad_top(lines: list[str], height: int) -> list[str]:
    """Pad ``lines`` to exactly ``height`` rows by prepending blank ones.

    Bar graphs grow upward from a bottom baseline, so blank rows go on top to
    keep that baseline aligned to the last row. If ``lines`` is taller than
    ``height`` (shouldn't happen once scaling caps, but defensively) the
    bottom ``height`` rows are kept.
    """
    if len(lines) > height:
        return lines[-height:]
    pad = height - len(lines)
    return [""] * pad + lines if pad > 0 else lines


def render_sparkline(values: list[float], height: int = 3, vmax: float | None = None) -> str:
    """A braille bar sparkline of ``values`` as a ``height``-line string.

    ``horizontal_graph`` draws one braille row per 4 units of value, so values
    are scaled so the graph is exactly ``height`` rows tall. ``vmax`` pins the
    scale (e.g. ``100`` for a percentage); ``None`` uses the window's maximum.
    A non-zero value always renders at least one unit so small percentages
    stay visible on a fixed scale. Bars bottom-align: the baseline is the last
    row. Values beyond the scale cap (e.g. CPU > 100%) never grow the chart
    past ``height`` rows.
    """
    if not values:
        return "\n".join([""] * height)
    top = vmax if vmax else max(values)
    if top <= 0:
        return "\n".join([""] * height)
    units = height * _ROWS_PER_UNIT
    scaled = [min(units, max(1, round(value / top * units))) if value > 0 else 0 for value in values]
    return "\n".join(_pad_top(horizontal_graph(scaled).split("\n"), height))


#: Left/right braille columns, top-to-bottom dot bit masks.
_LEFT_COL = (0x01, 0x02, 0x04, 0x40)
_RIGHT_COL = (0x08, 0x10, 0x20, 0x80)


def _mirror_col(bits: int, column: tuple[int, int, int, int]) -> int:
    """Mirror a column's 4 dots vertically within one braille row."""
    mirrored = 0
    for source, target in zip(column, reversed(column), strict=False):
        if bits & source:
            mirrored |= target
    return mirrored


def _mirror_cell(char: str) -> str:
    """Vertically mirror one braille character within its row."""
    code = ord(char) - 0x2800
    left = code & 0x47
    right = code & 0xB8
    return chr(0x2800 | _mirror_col(left, _LEFT_COL) | _mirror_col(right, _RIGHT_COL))


def _mirror_line(line: str) -> str:
    return "".join(_mirror_cell(char) for char in line)


def render_dual_sparkline(down: list[float], up: list[float], height: int = 3) -> str:
    """A two-direction braille sparkline of ``(down, up)`` samples.

    Renders ``2 * height`` rows: the ``up`` bars grow upward from a central
    baseline in the top half and the ``down`` bars grow downward in the bottom
    half. Both halves share the window's maximum so the in/out ratio stays
    honest; non-zero values always render at least one unit.
    """
    if not down or not up:
        return "\n".join([""] * (2 * height))
    top = max(down + up)
    if top <= 0:
        return "\n".join([""] * (2 * height))
    units = height * _ROWS_PER_UNIT
    scale = lambda value: min(units, max(1, round(value / top * units))) if value > 0 else 0  # noqa: E731
    up_rows = _pad_top(horizontal_graph([scale(v) for v in up]).split("\n"), height)
    down_rows = _pad_top(horizontal_graph([scale(v) for v in down]).split("\n"), height)
    bottom_rows = [_mirror_line(line) for line in reversed(down_rows)]
    return "\n".join(up_rows + bottom_rows)


def metric_duo(data: dict, name: str) -> tuple[float, float] | None:
    """``(down, up)`` numeric samples for two-direction metrics.

    Network maps ``inputMb``/``outputMb`` and block maps ``readMb``/``writeMb``
    to down/up. Returns ``None`` for other metrics or missing samples.
    """
    if name not in ("network", "block"):
        return None
    entry = data.get(name) or {}
    value = entry.get("value")
    if value is None:
        return None
    if name == "network":
        down = float(value.get("inputMb", 0) or 0)
        up = float(value.get("outputMb", 0) or 0)
    else:
        down = float(value.get("readMb", 0) or 0)
        up = float(value.get("writeMb", 0) or 0)
    return down, up


#: Sparkline scale cap per metric (``None`` = relative to the window's max).
METRIC_SCALE: dict[str, float | None] = {
    "cpu": 100,
    "memory": 100,
    "disk": 100,
    "network": None,
    "block": None,
}


def _parse_percent(text) -> float | None:
    try:
        return float(str(text).rstrip("%"))
    except (ValueError, AttributeError):
        return None


_BYTE_UNITS = {
    "": 1,
    "B": 1,
    "K": 1024,
    "KB": 1024,
    "KIB": 1024,
    "M": 1024**2,
    "MB": 1024**2,
    "MIB": 1024**2,
    "G": 1024**3,
    "GB": 1024**3,
    "GIB": 1024**3,
    "T": 1024**4,
    "TB": 1024**4,
    "TIB": 1024**4,
}


def _parse_bytes(text) -> float | None:
    """Parse a byte size like ``"252.4MiB"`` into bytes."""
    match = re.match(r"\s*([\d.]+)\s*([KMGTP]?i?B)?", str(text))
    if not match:
        return None
    value = float(match.group(1))
    unit = (match.group(2) or "").upper()
    return value * _BYTE_UNITS.get(unit, 1)


def _cpu_value(value) -> float | None:
    return _parse_percent(value)


def _mem_value(value) -> float | None:
    used = _parse_bytes(value.get("used"))
    total = _parse_bytes(value.get("total"))
    return used / total * 100 if used is not None and total else None


def _net_value(value) -> float:
    return float(value.get("inputMb", 0) or 0) + float(value.get("outputMb", 0) or 0)


def _block_value(value) -> float:
    return float(value.get("readMb", 0) or 0) + float(value.get("writeMb", 0) or 0)


def _disk_value(value) -> float | None:
    return _parse_percent(value.get("diskUsedPercentage"))


def _cpu_text(value) -> str:
    return str(value)


def _mem_text(value) -> str:
    return f"{value.get('used', '-')}/{value.get('total', '-')}"


def _net_text(value) -> str:
    return f"{value.get('inputMb', 0)}MB\u2193 {value.get('outputMb', 0)}MB\u2191"


def _block_text(value) -> str:
    return f"{value.get('readMb', 0)}MB\u2193 {value.get('writeMb', 0)}MB\u2191"


def _disk_text(value) -> str:
    raw = value.get("diskUsedPercentage", "-")
    if raw == "-":
        return "-"
    return f"{str(raw).rstrip('%')}%"


_VALUE_EXTRACTORS = {
    "cpu": _cpu_value,
    "memory": _mem_value,
    "network": _net_value,
    "block": _block_value,
    "disk": _disk_value,
}

_TEXT_FORMATTERS = {
    "cpu": _cpu_text,
    "memory": _mem_text,
    "network": _net_text,
    "block": _block_text,
    "disk": _disk_text,
}


def metric_value(data: dict, name: str) -> float | None:
    """Extract a numeric sample for a metric from a stats payload."""
    entry = data.get(name) or {}
    value = entry.get("value")
    if value is None:
        return None
    extractor = _VALUE_EXTRACTORS.get(name)
    return extractor(value) if extractor else None


def metric_value_text(data: dict, name: str) -> str:
    """A short current-value label for a metric."""
    entry = data.get(name) or {}
    value = entry.get("value")
    if value is None:
        return "-"
    formatter = _TEXT_FORMATTERS.get(name)
    return formatter(value) if formatter else "-"


def _format_total(mb: float) -> str:
    """A compact cumulative size label (GB, MB or KB)."""
    if mb >= 1024:
        return f"{mb / 1024:.1f}GB"
    if mb >= 1:
        return f"{mb:.0f}MB"
    return f"{mb * 1024:.0f}KB"


def format_duo_total_label(down: float, up: float) -> str:
    """Cumulative down/up totals, e.g. ``61.4GB↓/14.2GB↑``."""
    return f"{_format_total(down)}\u2193/{_format_total(up)}\u2191"
