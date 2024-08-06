"""Dokli CLI."""

import json
from typing import Annotated, Optional

import rel
import typer
import websocket
from openapi_client.api_response import ApiResponse
from openapi_client.rest import ApiException
from pydantic import ValidationError
from rich import print as rprint

from dokli.commands import ApiEntity, ApiVerb, get_entity_commands, run_command
from dokli.config import Config
from dokli.formatting import Format, format_data, format_response
from dokli.tui import app as tui

app = typer.Typer()


@app.command(name="api")
def api_command(
    connection_name: str,
    entity: ApiEntity,
    verb: ApiVerb,
    param: Annotated[Optional[list[str]], typer.Option("--param", "-p")] = None,  # noqa: UP007
    format: Format = Format.yaml,
) -> None:
    """API."""
    if verb is ApiVerb.verbs:
        rprint(format_data(get_entity_commands(entity), format))
        return
    config = Config()
    connection = config.get_connection(connection_name)
    response = run_command(connection=connection, entity=entity, verb=verb, params=param)
    match response:
        case ApiResponse():
            rprint(format_response(response, format=format))
        case ApiException():
            rprint(f"[red]{response}[/red]")
            raise typer.Exit(code=1)
        case ValidationError():
            rprint("[bold red]ValidationError:[/bold red]")
            rprint(response)
            raise typer.Exit(code=1)
        case _:
            raise ValueError(f"Unknown response type {type(response)}")


@app.command(name="logs")
def logs_command(connection_name: str, container_id: str, tail: int = 40) -> None:
    """Logs monitoring."""
    config = Config()
    connection = config.get_connection(connection_name)
    response = run_command(
        connection=connection,
        entity=ApiEntity.docker,
        verb=ApiVerb.getConfig,
        params=[container_id],
    )
    rprint(json.loads(response.raw_data))
    return
    if isinstance(response, ApiException):
        rprint(f"[red]{response}[/red]")
        raise typer.Exit(code=1)

    def on_message(ws, message):
        print(message)

    def on_error(ws, error):
        print(error)

    def on_close(ws, close_status_code, close_msg):
        print("### closed ###")

    def on_open(ws):
        # print("Opened connection")
        pass

    websocket.enableTrace(True)
    ws_url = str(connection.url).replace("http", "ws")
    ws = websocket.WebSocketApp(
        f"{ws_url}docker-container-logs?containerId={container_id}&tail={tail}",
        header={
            "Cookie": (response.headers or {}).get("Cookie", ""),
        },
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
    )

    ws.run_forever(
        dispatcher=rel, reconnect=5
    )  # Set dispatcher to automatic reconnection, 5 second reconnect delay if connection closed unexpectedly
    rel.signal(2, rel.abort)  # Keyboard Interrupt
    rel.dispatch()

    @app.command(name="tui")
    def tui_command() -> None:
        """Text User Interface."""
        config = Config()
        tui.config = config
        tui.run()


@app.callback(no_args_is_help=True)
def main():
    """Magical Dokploy CLI/TUI."""
