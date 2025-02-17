"""OpenAPI CLI."""

import re
from inspect import Parameter, Signature
from typing import Annotated, Any

import typer
from httpx import HTTPError, Response
from rich import print as rprint

from dokli.clients.api_client import APIClient
from dokli.commands import run_command
from dokli.formatting import Format, format_response

OPENAPI_TO_PYTHON = {
    "string": str,
    "integer": int,
    "number": float,
    "boolean": bool,
    "array": list,
    "object": str,
}


def _infer_param_type(param: dict[str, Any]):
    """Infiera el tipo Python a partir de OpenAPI."""
    schema = param.get("schema", {})
    param_type = schema.get("type", "string")  # Por defecto, string
    return OPENAPI_TO_PYTHON.get(param_type, str)


def _camel_case_to_snake_case(camel_case_str):
    return re.sub(r"(?<!^)(?=[A-Z])", "_", camel_case_str).lower()


def _api_command_factory(connection, route, method="GET", params=None, request_body=None, client=None):
    # Create a list of parameters for the signature
    param_hints = {p["name"]: _infer_param_type(p) for p in params}
    original_name = {_camel_case_to_snake_case(x["name"]): x["name"] for x in params}
    parameters = [
        Parameter(_camel_case_to_snake_case(name), Parameter.KEYWORD_ONLY, annotation=typ)
        for name, typ in param_hints.items()
    ]
    if request_body and request_body.get("required", False):
        parameters.append(
            Parameter("body", Parameter.KEYWORD_ONLY, annotation=Annotated[str, typer.Option(help="JSON body")])
        )
    # add format parameter
    parameters.append(Parameter("format", Parameter.KEYWORD_ONLY, default=Format.json, annotation=Format))
    # Create a Signature object
    sig = Signature(parameters)

    def api_command(format=Format.json, **kwargs):
        params = {original_name.get(x, x): v for x, v in kwargs.items()}
        response = run_command(
            connection=connection,
            method=method,
            route=route,
            params=params,
            client=client,
        )
        match response:
            case Response():
                rprint(format_response(response, format=format))
            case HTTPError():
                rprint(f"[red]{response}[/red]")
                raise typer.Exit(code=1)
            case _:
                raise ValueError(f"Unknown response type {type(response)}")

    api_command.__signature__ = sig
    return api_command


def _register_api_methods(connection):
    """Create a Typer app for each entity in the API schema.

    Given that Dokploy uses a entity.Action convention for API endpoints,
    we can use the entity name as the Typer app name and the action name as the command.
    """
    _app = typer.Typer()
    client = APIClient(connection)
    paths = client.schema.get("paths", {})

    entity_apps = {}

    # iterate over the paths to register commands
    for route, methods in paths.items():
        entity, action = (_camel_case_to_snake_case(x) for x in route.strip("/").split("."))
        if entity not in entity_apps:
            entity_app = typer.Typer()
            entity_apps[entity] = entity_app
        else:
            entity_app = entity_apps[entity]
        for method, details in methods.items():
            params = details.get("parameters", [])
            request_body = details.get("requestBody", {})
            description = details.get("description", "")
            summary = details.get("summary", "")

            func = _api_command_factory(connection, route, method.upper(), params, request_body, client=client)
            func.__doc__ = " ".join(x for x in [summary, description] if x)
            entity_app.command(name=action)(func)

    # register entity apps as sub commands of the connection app
    for entity, entity_app in entity_apps.items():

        def _entity_app_callback():
            pass

        _entity_app_callback.__doc__ = f"Show {entity} commands."

        entity_app.callback(no_args_is_help=True)(_entity_app_callback)
        _app.add_typer(entity_app, name=entity)

    def _app_callback():
        pass

    _app_callback.__doc__ = f"[{connection.name}] Dokploy Instance API"

    _app.callback(no_args_is_help=True)(_app_callback)
    return _app


def register_connections(app, config):
    """Register the API methods for each connection in config."""
    for connection in config.connections:
        try:
            connection_app = _register_api_methods(connection)
            app.add_typer(connection_app, name=connection.name)
        except Exception as e:
            rprint(f"[red]Error registering API methods: {e}[/red]")
            raise
