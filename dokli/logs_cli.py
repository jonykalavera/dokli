"""The ``dokli logs`` command: service logs via REST (one-shot) or WebSocket (follow)."""

import asyncio
from collections.abc import Callable
from typing import Any

import typer
import websockets
from rich import print as rprint

from dokli.api_client import APIClient
from dokli.config import Config, ConnectionConfig, complete_connection_names, resolve_connection
from dokli.wss import DEPLOYMENT_LOGS_ENDPOINT, LOGS_ENDPOINT, iter_lines

#: Dokploy's ``readLogs`` tail bound (OpenAPI ``minimum``/``maximum``).
MAX_TAIL = 10000


def build_command(config: Config) -> Callable[..., None]:
    """Return the ``logs`` command function, bound to ``config``."""

    def logs_command(
        connection_name: str | None = typer.Argument(
            None, help="Connection name.", shell_complete=complete_connection_names
        ),
        compose_id: str = typer.Option(None, "--compose-id", help="Compose service id."),
        application_id: str = typer.Option(None, "--application-id", help="Application service id."),
        deployment_id: str = typer.Option(None, "--deployment-id", help="Deployment id."),
        container_id: str = typer.Option(None, "--container-id", help="Docker container id (with --compose-id)."),
        lines: int = typer.Option(100, "-n", "--lines", help="Number of lines (history)."),
        follow: bool = typer.Option(False, "-f", "--follow", help="Follow the log (stream live)."),
    ) -> None:
        """Show a service's last -n log lines, or stream them live with -f.

        Note: deployment -f streams the whole deployment log (its endpoint has
        no tail limit), so -n does not cap it.
        """
        connection = resolve_connection(config, connection_name)
        if sum(bool(x) for x in (compose_id, application_id, deployment_id)) != 1:
            raise typer.BadParameter("Provide exactly one of --compose-id, --application-id, --deployment-id.")
        if compose_id and not container_id:
            raise typer.BadParameter("--container-id is required with --compose-id.")
        if lines < 1 or lines > MAX_TAIL:
            raise typer.BadParameter(f"-n/--lines must be between 1 and {MAX_TAIL}.")
        if follow:
            asyncio.run(
                _follow_service_logs(connection, compose_id, application_id, deployment_id, container_id, lines)
            )
        else:
            asyncio.run(
                _fetch_service_logs(connection, compose_id, application_id, deployment_id, container_id, lines)
            )

    return logs_command


def _request(connection: ConnectionConfig, route: str, params: dict) -> Any:
    """Run a REST read and return the raw JSON payload."""
    return APIClient(connection).request("GET", route, params).json()


async def _fetch_service_logs(
    connection: ConnectionConfig,
    compose_id: str | None,
    application_id: str | None,
    deployment_id: str | None,
    container_id: str | None,
    lines: int,
) -> None:
    """Print a service's last ``lines`` log lines (one-shot REST read)."""
    if compose_id:
        text = await asyncio.to_thread(
            _request, connection, "compose.readLogs",
            {"composeId": compose_id, "containerId": container_id, "tail": lines},
        )
    elif application_id:
        text = await asyncio.to_thread(
            _request, connection, "application.readLogs", {"applicationId": application_id, "tail": lines}
        )
    else:
        text = await asyncio.to_thread(
            _request, connection, "deployment.readLogs", {"deploymentId": deployment_id, "tail": lines}
        )
    print(text.rstrip("\n"))  # noqa: T201


async def _follow_service_logs(
    connection: ConnectionConfig,
    compose_id: str | None,
    application_id: str | None,
    deployment_id: str | None,
    container_id: str | None,
    lines: int,
) -> None:
    """Stream a service's logs live over its WebSocket endpoint."""
    server_id = None
    if compose_id:
        compose = await asyncio.to_thread(_request, connection, "compose.one", {"composeId": compose_id})
        server_id = compose.get("serverId")
        endpoint = LOGS_ENDPOINT
        params = {"containerId": container_id, "tail": lines}
    elif application_id:
        application = await asyncio.to_thread(
            _request, connection, "application.one", {"applicationId": application_id}
        )
        app_name = application.get("appName")
        if not app_name:
            raise typer.BadParameter("Application has no appName.")
        server_id = application.get("serverId")
        containers = await asyncio.to_thread(
            _request,
            connection,
            "docker.getContainersByAppNameMatch",
            {"appName": app_name, **({"serverId": server_id} if server_id else {})},
        )
        running = [c for c in containers if isinstance(c, dict) and c.get("state") == "running"] or containers
        if not running:
            raise typer.BadParameter(f"No container found for application '{app_name}'.")
        endpoint = LOGS_ENDPOINT
        params = {"containerId": running[0]["containerId"], "tail": lines}
    else:
        deployments = await asyncio.to_thread(_request, connection, "deployment.allCentralized", {})
        deployment = next((d for d in deployments if d.get("deploymentId") == deployment_id), None)
        if deployment is None or not deployment.get("logPath"):
            raise typer.BadParameter("Deployment not found or has no log.")
        server_id = deployment.get("serverId")
        endpoint = DEPLOYMENT_LOGS_ENDPOINT
        params = {"logPath": deployment["logPath"]}
    if server_id:
        params["serverId"] = server_id
    try:
        async for raw in iter_lines(connection, endpoint, params):
            print(raw.rstrip("\r"), flush=True)  # noqa: T201
    except KeyboardInterrupt:
        pass
    except websockets.exceptions.ConnectionClosed:
        pass  # the stream ended (e.g. the container stopped)
    except (websockets.exceptions.WebSocketException, OSError) as err:
        rprint(f"[red]Log stream failed: {err}[/red]")
        raise typer.Exit(code=1) from None
