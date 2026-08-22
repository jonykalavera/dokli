"""WebSocket helpers for Dokploy's real-time endpoints.

Dokploy streams live data over raw WebSocket endpoints (one per feature) on the
host root — NOT under ``/api`` — authenticated with the same ``x-api-key``
header the REST API uses. See Dokploy's ``apps/dokploy/server/wss/`` for the
server side.
"""

import json
from collections.abc import AsyncIterator
from urllib.parse import urlencode

from websockets.asyncio.client import connect

from dokli.config import ConnectionConfig

#: Live container logs (``docker logs --timestamps --follow``).
LOGS_ENDPOINT = "/docker-container-logs"
#: Live deployment/build logs (``tail -f`` of the deployment log file).
DEPLOYMENT_LOGS_ENDPOINT = "/listen-deployment"
#: Live container stats (JSON pushed every ~1.3s).
STATS_ENDPOINT = "/listen-docker-stats-monitoring"


def ws_base(connection: ConnectionConfig) -> str:
    """The ``wss://`` base for a connection (host root, no ``/api``)."""
    base = str(connection.url).rstrip("/")
    return base.replace("https://", "wss://").replace("http://", "ws://")


def ws_url(connection: ConnectionConfig, path: str, params: dict | None = None) -> str:
    """A WebSocket URL for a Dokploy endpoint, with query params."""
    query = urlencode(params or {})
    return f"{ws_base(connection)}{path}" + (f"?{query}" if query else "")


def _headers(connection: ConnectionConfig) -> dict[str, str]:
    return {"x-api-key": connection.get_api_key()}


async def iter_lines(connection: ConnectionConfig, path: str, params: dict | None = None) -> AsyncIterator[str]:
    """Stream a Dokploy WebSocket endpoint, yielding complete lines.

    The server sends raw chunks that may span or split lines, so partial lines
    are buffered until a newline arrives. Raises the underlying exception
    (``websockets``/``httpx``) when the handshake is rejected or the connection
    fails, letting callers fall back to the polling API.
    """
    uri = ws_url(connection, path, params)
    buffer = ""
    async with connect(uri, additional_headers=_headers(connection)) as ws:
        async for chunk in ws:
            message = chunk.decode("utf-8", errors="replace") if isinstance(chunk, bytes) else chunk
            text = buffer + message
            *lines, buffer = text.split("\n")
            for line in lines:
                yield line


async def iter_stats(
    connection: ConnectionConfig, app_name: str, app_type: str = "application"
) -> AsyncIterator[dict]:
    """Stream container stats, yielding each ``data`` payload as a dict.

    The server pushes ``{"data": {cpu, memory, disk, network, block}}`` every
    ~1.3s; each metric is the latest sample (``{"value": ..., "time": ...}``) or
    ``None``. Raises the underlying exception when the handshake fails.
    """
    uri = ws_url(connection, STATS_ENDPOINT, {"appName": app_name, "appType": app_type})
    async with connect(uri, additional_headers=_headers(connection)) as ws:
        async for chunk in ws:
            message = chunk.decode("utf-8", errors="replace") if isinstance(chunk, bytes) else chunk
            try:
                payload = json.loads(message)
            except json.JSONDecodeError:
                continue
            data = payload.get("data") if isinstance(payload, dict) else None
            if isinstance(data, dict):
                yield data
