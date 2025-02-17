"""Dokli commands."""

import json
import re

from httpx import HTTPError, Response
from pydantic import ValidationError

from dokli.clients.api_client import APIClient
from dokli.config import ConnectionConfig

PARAM_REGEX = re.compile(r"^((?P<key>[a-z][a-z0-9_]+)=)?(?P<value>.+)$")


MAGIC_JSON = "%json:"
MAGIC_FILE = "%file:"


def _parse_params(params: dict[str, str]) -> dict[str, str]:
    """Parse CLI params."""
    kwargs = {}
    for key, value in params.items():
        _value = value
        if value.startswith(MAGIC_JSON):
            _value = json.loads(value[len(MAGIC_JSON) :])
        if value.startswith(MAGIC_FILE):
            with open(value[len(MAGIC_FILE) :]) as f:
                _value = json.load(f)
        kwargs[key] = _value
    return kwargs


def run_command(
    connection: ConnectionConfig,
    method: str,
    route: str,
    params: dict[str, str] | None = None,
    client: APIClient | None = None,
) -> HTTPError | Response | ValidationError:
    """Run a dokploy API command using Dokli connection."""
    api_client = client or APIClient(connection)
    # Enter a context with an instance of the API client
    # Create an instance of the API class
    kwargs = _parse_params(params or {})

    try:
        return api_client.request(method, route, kwargs)
    except HTTPError as err:
        return err
    except ValidationError as err:
        return err
