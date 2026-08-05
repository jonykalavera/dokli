"""Shared action confirmation and execution helpers."""

from collections.abc import Callable
from typing import Any

import httpx
from pydantic import SecretBytes, SecretStr

from dokli.api_client import APIClient
from dokli.config import ConnectionConfig
from dokli.tui.engine import DESTRUCTIVE_VERBS, EntityAction
from dokli.tui.screens.generic.confirm import ConfirmScreen


def build_body(action: EntityAction, data: dict) -> dict:
    """Build a request body from form data, dropping empties and unwrapping secrets."""
    body = {}
    for key, raw_value in data.items():
        if raw_value in ("", None):
            continue
        value = (
            raw_value.get_secret_value()
            if isinstance(raw_value, SecretStr | SecretBytes)
            else raw_value
        )
        body[key] = value
    return body


def confirm_and_run(
    screen,
    connection: ConnectionConfig,
    action: EntityAction,
    body: dict,
    on_success: Callable[[], Any] | None = None,
) -> None:
    """Ask for explicit confirmation, then run the action."""
    summary = ", ".join(f"{key}={value}" for key, value in body.items()) or "(no body)"
    danger = action.verb in DESTRUCTIVE_VERBS
    screen.app.push_screen(
        ConfirmScreen(title=f"Run {action.route}?", message=summary, danger=danger),
        callback=lambda confirmed: _run(screen, connection, action, body, on_success) if confirmed else None,
    )


def _run(
    screen,
    connection: ConnectionConfig,
    action: EntityAction,
    body: dict,
    on_success: Callable[[], Any] | None,
) -> None:
    client = APIClient(connection)
    params: dict = {"body": body} if body else {}
    try:
        client.request(action.method, action.route, params)
    except httpx.HTTPError as err:
        screen.notify(f"API error: {err}", severity="error", timeout=10)
        return
    screen.notify(f"{action.route} OK")
    if on_success:
        on_success()
