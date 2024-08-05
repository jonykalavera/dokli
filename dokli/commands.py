"""Dokli commands."""

import json
import re

import openapi_client
from openapi_client.api_response import ApiResponse
from openapi_client.rest import ApiException
from pydantic import ValidationError

from dokli.api_commands_config import API_ENTITY_MAP, API_VERB_MAP, ApiEntity, ApiVerb
from dokli.config import ConnectionConfig

PARAM_REGEX = re.compile(r"^((?P<key>[a-z][a-z0-9_]+)=)?(?P<value>.+)$")


MAGIC_JSON = "%json:"
MAGIC_FILE = "%file:"


def _parse_params(params: list[str]) -> tuple[list[str], dict[str, str]]:
    """Parse CLI params."""
    args = []
    kwargs = {}
    for param in params:
        if not (match := PARAM_REGEX.match(param)):
            raise ValueError(f"Invalid param {param}")
        value = match.group("value")
        key = match.group("key")
        if isinstance(value, str) and value.startswith(MAGIC_JSON):
            value = json.loads(value[len(MAGIC_JSON) :])
        if isinstance(value, str) and value.startswith(MAGIC_FILE):
            with open(value[len(MAGIC_FILE) :]) as f:
                value = json.load(f)
        if key:
            kwargs[key] = value
        else:
            args.append(value)
    return args, kwargs


def get_entity_commands(entity: ApiEntity) -> list[str]:
    """Return a list of commands for an entity."""
    return [verb.value for verb in API_VERB_MAP[entity]]


def run_command(
    connection: ConnectionConfig, entity: ApiEntity, verb: ApiVerb, params: list[str] | None = None
) -> ApiException | ApiResponse | ValidationError:
    """Run a dokploy API command using Dokli connection."""
    configuration = openapi_client.Configuration(host=f"{connection.url}/api")

    # Configure Bearer authorization: Authorization
    configuration = openapi_client.Configuration(access_token=connection.api_key.get_secret_value())

    # Enter a context with an instance of the API client
    with openapi_client.ApiClient(configuration) as api_client:
        # Create an instance of the API class
        api_instance = API_ENTITY_MAP[entity](api_client)
        api_method_name = API_VERB_MAP[entity][verb]
        api_method = getattr(api_instance, api_method_name)
        args, kwargs = _parse_params(params or [])

        try:
            return api_method(*args, **kwargs)
        except ApiException as err:
            return err
        except ValidationError as err:
            return err
