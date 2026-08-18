"""Generate README screenshots from the TUI.

Runs the app headless against the fake, anonymized test data (``FAKE_SCHEMA`` +
mocked responses from ``tests/test_tui.py``) — never against a real connection
— and exports each screen as an SVG into ``assets/``.

Usage:
    uv run python tools/screenshots.py
"""

import asyncio
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
    async with app.run_test(size=SIZE) as pilot:
        app.install_screen(SplashScreen(), name="splash")
        app.push_screen("splash")
        await _settle(pilot)
        return _save(app, "splash")


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
