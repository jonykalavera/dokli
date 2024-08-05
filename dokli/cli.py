"""Dokli CLI."""

import json
from typing import Annotated, Optional

import typer
from openapi_client.api_response import ApiResponse
from openapi_client.rest import ApiException
from pydantic import ValidationError
from rich import print as rprint

from dokli.commands import ApiEntity, ApiVerb, get_entity_commands, run_command
from dokli.config import Config
from dokli.formatting import Format, format_data, format_response
from dokli.tui import app as tui

app = typer.Typer()


@app.command()
def api(
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
            if response.data:
                rprint(response.data)
            elif response.body:
                data = json.loads(response.body)
                rprint(f"[red]{format_data(data, format)}[/red]")
            raise typer.Exit(code=1)
        case ValidationError():
            rprint("[bold red]ValidationError:[/bold red]")
            rprint(response)
            raise typer.Exit(code=1)
        case _:
            raise ValueError(f"Unknown response type {type(response)}")


@app.callback(invoke_without_command=True)
def main():
    """Magical Dokploy CLI/TUI.

    No commands, launches the TUI.
    """
    tui.run()