"""OpenAPI CLI."""

import keyword
import re
import sys
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from inspect import Parameter, Signature
from typing import Annotated, Any

import typer
from httpx import HTTPError, Response
from rich import print as rprint

from dokli.api_client import APIClient
from dokli.commands import run_command
from dokli.config import Config, ConnectionConfig
from dokli.formatting import Format, format_response

OPENAPI_TO_PYTHON: dict[str, type] = {
    "string": str,
    "integer": int,
    "number": float,
    "boolean": bool,
    "array": list,
    "object": str,
}


class HTTPMethod(str, Enum):
    """HTTP Method enumeration."""

    GET = "GET"
    HEAD = "HEAD"
    POST = "POST"
    PATCH = "PATCH"
    DELETE = "DELETE"


@dataclass
class APIRequest:
    """API Request data object."""

    route: str
    method: str = HTTPMethod.GET.value
    params: list[dict[str, Any]] | None = None
    body: dict[str, Any] | None = None


def _infer_param_type(param: dict[str, Any]) -> type:
    """Infer the type of a parameter from OpenAPI."""
    schema = param.get("schema", {})
    param_type = schema.get("type", "string")  # Por defecto, string
    return OPENAPI_TO_PYTHON.get(param_type, str)


def _camel_case_to_snake_case(camel_case_str: str) -> str:
    """Convert camelCase to snake_case."""
    return re.sub(r"(?<!^)(?=[A-Z])", "_", camel_case_str).lower()


def _safe_param_name(name: str) -> str:
    """Return a valid Python parameter name for an OpenAPI parameter.

    Some schemas use reserved words (e.g. ``from``) or characters that are not
    valid in Python identifiers. Invalid names are prefixed with ``p_``.
    """
    name = _camel_case_to_snake_case(name)
    name = re.sub(r"\W", "_", name)
    if keyword.iskeyword(name) or not name.isidentifier():
        name = f"p_{name}"
    return name


def _api_command_factory(
    connection: ConnectionConfig,
    request: APIRequest,
    client: APIClient | None = None,
) -> Callable[..., None]:
    """Create a command from an OpenAPI endpoint."""
    params = request.params or []
    # Create a list of parameters for the signature
    original_name = {_safe_param_name(x["name"]): x["name"] for x in params}
    param_hints = {_safe_param_name(p["name"]): _infer_param_type(p) for p in params}
    parameters = [Parameter(name, Parameter.KEYWORD_ONLY, annotation=typ) for name, typ in param_hints.items()]
    if request.body and request.body.get("required", False):
        parameters.append(
            Parameter("body", Parameter.KEYWORD_ONLY, annotation=Annotated[str, typer.Option(help="JSON body")])
        )
    # add format parameter
    parameters.append(Parameter("format", Parameter.KEYWORD_ONLY, default=Format.yaml, annotation=Format))
    # add secrets parameter
    parameters.append(
        Parameter(
            "show_secrets",
            Parameter.KEYWORD_ONLY,
            default=False,
            annotation=bool,
        )
    )
    # Create a Signature object
    sig = Signature(parameters)

    def api_command(format: Format = Format.json, show_secrets: bool = False, **kwargs: Any) -> None:
        params = {original_name.get(x, x): v for x, v in kwargs.items()}
        response = run_command(
            connection=connection,
            method=request.method,
            route=request.route,
            params=params,
            client=client,
        )
        match response:
            case Response():
                rprint(format_response(response, format=format, show_secrets=show_secrets))
            case HTTPError():
                rprint(f"[red]{response}[/red]")
                raise typer.Exit(code=1)
            case _:
                raise ValueError(f"Unknown response type {type(response)}")

    api_command.__signature__ = sig  # ty: ignore[unresolved-attribute]
    return api_command


def _register_api_methods(connection: ConnectionConfig) -> typer.Typer:
    """Create a Typer app for each entity in the API schema.

    Given that Dokploy uses a entity.Action convention for API endpoints,
    we can use the entity name as the Typer app name and the action name as the command.
    """
    _app = typer.Typer(name=connection.name, help=f"Dokploy Instance: {connection.url}")
    client = APIClient(connection)
    paths = client.schema.get("paths", {})

    entity_apps: dict[str, typer.Typer] = {}

    # iterate over the paths to register commands
    for route, methods in paths.items():
        entity, action = (_camel_case_to_snake_case(x) for x in route.strip("/").split("."))
        if entity not in entity_apps:
            entity_app = typer.Typer(name=entity, help=f"{entity} commands")
            entity_apps[entity] = entity_app
        else:
            entity_app = entity_apps[entity]
        for method, details in methods.items():
            params = details.get("parameters", [])
            request_body = details.get("requestBody", {})
            description = details.get("description", "")
            summary = details.get("summary", "")

            api_request = APIRequest(route, method.upper(), params, request_body)
            func = _api_command_factory(connection, api_request, client=client)
            entity_app.command(name=action, help=" ".join(x for x in [summary, description] if x))(func)

    # register entity apps as sub commands of the connection app
    for entity, entity_app in entity_apps.items():
        entity_app.callback(no_args_is_help=True)(lambda: None)
        _app.add_typer(entity_app, name=entity)

    _app.callback(no_args_is_help=True)(lambda: None)
    return _app


def build_command(config: Config) -> typer.Typer:
    """Register the API methods for each connection in config.

    A connection whose API key cannot be resolved (e.g. a failing
    ``api_key_cmd``) is skipped with a warning instead of breaking the CLI.
    """
    app = typer.Typer(name="api", help="API commands")
    app.callback(no_args_is_help=True)(lambda: None)
    for connection in config.connections:
        try:
            connection_app = _register_api_methods(connection)
            app.add_typer(connection_app, name=connection.name)
        except Exception as e:
            rprint(f"[yellow]Skipping connection '{connection.name}': {e}[/yellow]", file=sys.stderr)
    return app
