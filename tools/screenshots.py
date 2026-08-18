"""Generate README screenshots from the TUI.

Runs the app headless against the fake, anonymized test data (``FAKE_SCHEMA`` +
mocked responses from ``tests/test_tui.py``) — never against a real connection
— and rasterizes each screen directly from Textual's compositor cell grid into a
PNG in ``assets/``.

Rasterizing the cell grid ourselves (instead of Textual's SVG export, which
serializes text as ``<text textLength>`` and depends on the viewer honoring the
metrics of Fira Code + Nerd Font glyphs) keeps the output faithful to a real
terminal: every character — box-drawing borders, Nerd Font icons, and the
icon↔text spacing — is drawn at its exact cell with a real Nerd Font, so the
README images look right for everyone regardless of installed fonts.

Requires Pillow and the Agave Nerd Font Mono (regular + bold).

Usage:
    uv run python tools/screenshots.py
"""

import asyncio
import sys
from pathlib import Path
from unittest import mock

from PIL import Image, ImageDraw, ImageFont
from rich.console import Console

from dokli.tui.app import DokliApp
from dokli.tui.engine import parse_spec
from dokli.tui.screens.generic.browser import BrowserScreen
from dokli.tui.screens.generic.result import ResultScreen
from dokli.tui.screens.splash import SplashScreen

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tests.test_tui import (  # noqa: E402
    FAKE_SCHEMA,
    FakeResponse,
    _config,
    _connection,
    _fake_requests,
    _select,
)

ASSETS = Path(__file__).resolve().parent.parent / "assets"
SIZE = (110, 32)
# The splash logo is 33 lines tall plus header/footer/status box, so it needs
# more rows than the default screenshot size to avoid clipping the art.
SIZE_SPLASH = (110, 40)

FONT_REGULAR = "/usr/share/fonts/TTF/AgaveNerdFontMono-Regular.ttf"
FONT_BOLD = "/usr/share/fonts/TTF/AgaveNerdFontMono-Bold.ttf"
FONT_SIZE = 20

# Fallbacks for cells without an explicit style (e.g. bare padding).
DEFAULT_FG = (200, 200, 205)
DEFAULT_BG = (49, 50, 68)

LOG_DATA = (
    "2026-08-05T19:55:54Z frigate started\n"
    "2026-08-05T19:55:55Z [detector] motion detected\n"
    "2026-08-05T19:56:00Z [events] snapshot saved\n"
    "2026-08-05T19:56:12Z [detector] motion cleared"
)


def _patch_api() -> list[mock._patch]:
    """Patch every APIClient site with the fake, anonymized responses."""
    client = mock.Mock(schema=FAKE_SCHEMA)
    responses = _fake_requests()

    def fake_request(method, path, params):
        return FakeResponse(responses.get(path, []))

    client.request.side_effect = fake_request
    return [
        mock.patch("dokli.tui.screens.generic.browser.APIClient", return_value=client),
        mock.patch("dokli.tui.app.APIClient", return_value=client),
        mock.patch("dokli.tui.screens.generic.execute.APIClient", return_value=client),
        mock.patch("dokli.tui.screens.generic.result.APIClient", return_value=client),
    ]


def _triplet(color, fallback):
    """A Rich color as an ``(r, g, b)`` tuple, falling back when unset/default."""
    if color is None:
        return fallback
    triplet = color.triplet
    if triplet is None:
        return fallback
    return (triplet.red, triplet.green, triplet.blue)


def _render_png(app: DokliApp, name: str) -> str:
    """Rasterize the screen's cell grid into ``assets/tui-<name>.png``."""
    width, height = app.size
    regular = ImageFont.truetype(FONT_REGULAR, FONT_SIZE)
    bold = ImageFont.truetype(FONT_BOLD, FONT_SIZE)
    cell_w = round(regular.getlength(" "))
    ascent, descent = regular.getmetrics()
    cell_h = ascent + descent

    console = Console(width=width, height=height, force_terminal=True, color_system="truecolor")
    renderable = app.screen._compositor.render_update(
        full=True, screen_stack=app._background_screens, simplify=True
    )
    lines = console.render_lines(
        renderable, console.options.update(width=width, height=height), style=None, pad=False
    )

    image = Image.new("RGB", (width * cell_w, height * cell_h), DEFAULT_BG)
    draw = ImageDraw.Draw(image)
    for row, line in enumerate(lines):
        col = 0
        for segment in line:
            if getattr(segment, "control", False):
                continue
            text = segment.text
            if text.startswith("\x1b["):
                continue
            style = segment.style
            fg = _triplet(style.color if style else None, DEFAULT_FG)
            bg = _triplet(style.bgcolor if style else None, DEFAULT_BG)
            font = bold if (style and style.bold) else regular
            for char in text:
                if char == "\n":
                    continue
                x0 = col * cell_w
                y0 = row * cell_h
                draw.rectangle([x0, y0, x0 + cell_w, y0 + cell_h], fill=bg)
                if char != " ":
                    draw.text((x0, y0 + ascent), char, font=font, fill=fg, anchor="ls")
                col += 1
    path = ASSETS / f"tui-{name}.png"
    image.save(str(path))
    return str(path)


async def _settle(pilot) -> None:
    for _ in range(12):
        await pilot.pause()


async def _wait_for_browser(app: DokliApp, pilot) -> None:
    for _ in range(100):
        await pilot.pause()
        if isinstance(app.screen, BrowserScreen):
            return
        await asyncio.sleep(0.02)
    raise RuntimeError("Browser never appeared")


async def shot_splash() -> str:
    """Render the splash screen."""
    app = DokliApp(config=_config())
    async with app.run_test(size=SIZE_SPLASH) as pilot:
        app.install_screen(SplashScreen(), name="splash")
        app.push_screen("splash")
        await _settle(pilot)
        app.sub_title = ""
        await _settle(pilot)
        return _render_png(app, "splash")


async def shot_connections() -> str:
    """Render the connections screen."""
    app = DokliApp(config=_config())
    async with app.run_test(size=SIZE) as pilot:
        await _settle(pilot)
        return _render_png(app, "connections")


async def shot_browser() -> str:
    """Render the browser screen."""
    app = DokliApp(config=_config())
    async with app.run_test(size=SIZE) as pilot:
        app.set_connection(_connection())
        await _wait_for_browser(app, pilot)
        return _render_png(app, "browser")


async def shot_browser_detail() -> str:
    """Render the browser detail screen."""
    app = DokliApp(config=_config())
    async with app.run_test(size=SIZE) as pilot:
        app.set_connection(_connection())
        await _wait_for_browser(app, pilot)
        _select(app, "project")
        await pilot.press("l")
        await _settle(pilot)
        _select(app, "media")
        await pilot.press("l")
        await _settle(pilot)
        _select(app, "production")
        await pilot.press("l")
        await _settle(pilot)
        _select(app, "torrents")
        await pilot.press("l")
        await _settle(pilot)
        return _render_png(app, "browser-detail")


async def shot_palette() -> str:
    """Render the palette screen."""
    app = DokliApp(config=_config())
    async with app.run_test(size=SIZE) as pilot:
        app.set_connection(_connection())
        await _wait_for_browser(app, pilot)
        await pilot.press("ctrl+p")
        await _settle(pilot)
        return _render_png(app, "palette")


async def shot_result() -> str:
    """Render the result screen."""
    app = DokliApp(config=_config())
    async with app.run_test(size=SIZE) as pilot:
        registry = parse_spec(FAKE_SCHEMA)
        action = registry.get("compose").get("readLogs")
        screen = ResultScreen(
            _connection(),
            action,
            LOG_DATA,
            params={"composeId": "c1", "containerId": "cc1"},
        )
        screen._follow = False
        app.install_screen(screen, name="result")
        app.push_screen("result")
        await _settle(pilot)
        return _render_png(app, "result")


SHOTS = {
    "splash": shot_splash,
    "connections": shot_connections,
    "browser": shot_browser,
    "browser-detail": shot_browser_detail,
    "palette": shot_palette,
    "result": shot_result,
}


def main() -> None:
    """Render every screenshot, printing the written files."""
    patchers = _patch_api()
    for patcher in patchers:
        patcher.start()
    try:
        for _name, shot in SHOTS.items():
            path = asyncio.run(shot())
            print(f"wrote {path}")  # noqa: T201
    finally:
        for patcher in patchers:
            patcher.stop()


if __name__ == "__main__":
    main()
