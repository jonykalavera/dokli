"""Generate README screenshots from the TUI.

Runs the app headless against the fake, anonymized test data (``FAKE_SCHEMA`` +
mocked responses from ``tests/test_tui.py``) — never against a real connection
— and exports each screen as an SVG into ``assets/``.

Usage:
    uv run python tools/screenshots.py
"""

import asyncio
import html
import re
import sys
from pathlib import Path
from unittest import mock

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


def _save(app: DokliApp, name: str) -> str:
    path = ASSETS / f"tui-{name}.svg"
    app.save_screenshot(str(path))
    return str(path)


_TEXT_ELEMENT = re.compile(r"<text(?P<attrs>[^>]*)>(?P<body>[^<]*)</text>")


def _rectify_logo_blocks(svg: str) -> str:
    """Render the splash logo's ``█`` glyphs as crisp ``<rect>`` cells.

    The exported SVG positions every character at fixed cell coordinates, but
    the actual rendering depends on the viewer honoring ``textLength`` and using
    a monospaced font (Fira Code via ``@font-face``); fallback fonts or renderers
    that ignore ``textLength`` compress the spaces and misalign the block art.
    Drawing the blocks as rects removes that dependency entirely.
    """
    fills = {k: v.strip() for k, v in re.findall(r"\.terminal-\w+-r(\d+)\s*\{\s*fill:\s*([^;}]+)", svg)}

    def replace(match: re.Match) -> str:
        attrs, body = match.group("attrs"), match.group("body")
        if "█" not in body:
            return match.group(0)
        text = html.unescape(body).replace("\u00a0", " ")
        cls = re.search(r'class="[^"]*-r(\d+)"', attrs).group(1)
        x = float(re.search(r'x="([\d.]+)"', attrs).group(1))
        y = float(re.search(r'y="([\d.]+)"', attrs).group(1))
        total = float(re.search(r'textLength="([\d.]+)"', attrs).group(1))
        cell = total / len(text) if text else 12.2
        fill = fills.get(cls, "#e4e4e6")
        top = y - 18.5  # baseline -> cell top (font-size 20 / line-height 24.4)
        rects = []
        for index, char in enumerate(text):
            if char == "█":
                rects.append(
                    f'<rect x="{x + index * cell:.1f}" y="{top:.1f}" '
                    f'width="{cell:.1f}" height="24.65" fill="{fill}" />'
                )
        return "".join(rects)

    return _TEXT_ELEMENT.sub(replace, svg)


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
        splash = app.screen
        app.sub_title = ""
        # The floating status box collides with the logo art in the centered
        # layout; it is transient anyway, so hide it for a clean logo shot.
        splash.query_one("#status-panel").display = False
        await _settle(pilot)
        svg = _rectify_logo_blocks(app.export_screenshot())
        path = ASSETS / "tui-splash.svg"
        path.write_text(svg)
        return str(path)


async def shot_connections() -> str:
    """Render the connections screen."""
    app = DokliApp(config=_config())
    async with app.run_test(size=SIZE) as pilot:
        await _settle(pilot)
        return _save(app, "connections")


async def shot_browser() -> str:
    """Render the browser screen."""
    app = DokliApp(config=_config())
    async with app.run_test(size=SIZE) as pilot:
        app.set_connection(_connection())
        await _wait_for_browser(app, pilot)
        return _save(app, "browser")


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
        return _save(app, "browser-detail")


async def shot_palette() -> str:
    """Render the palette screen."""
    app = DokliApp(config=_config())
    async with app.run_test(size=SIZE) as pilot:
        app.set_connection(_connection())
        await _wait_for_browser(app, pilot)
        await pilot.press("ctrl+p")
        await _settle(pilot)
        return _save(app, "palette")


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
        return _save(app, "result")


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
