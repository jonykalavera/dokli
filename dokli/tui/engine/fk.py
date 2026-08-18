"""Foreign-key form controls: FK field -> candidate source.

Action forms show ``*Id`` fields as raw id inputs. For FK fields that reference
a listable entity (e.g. ``serverId`` → ``server.all``) the form renders a
dropdown of candidates instead, falling back to free text when the source is
unavailable. Sources are curated here because the OpenAPI document does not
express these relations.
"""

import httpx

from dokli.api_client import APIClient
from dokli.config import ConnectionConfig
from dokli.tui.engine.introspect import record_title

# FK field name -> source spec. ``entity``+``verb`` form the list route (e.g.
# ``server.all``); ``value_field`` is the candidate's id key; ``filter_field``
# optionally narrows candidates (e.g. git providers by ``providerType``);
# ``params`` map query params to form-context keys. Sources with ``service``
# enumerate live services instead (see ``_load_service_candidates``). Fields
# without a curated source fall back to a plain text input.
FK_SOURCES: dict[str, dict] = {
    "serverId": {"entity": "server", "verb": "all", "value_field": "serverId"},
    "destinationId": {"entity": "destination", "verb": "all", "value_field": "destinationId"},
    "registryId": {"entity": "registry", "verb": "all", "value_field": "registryId"},
    "certificateId": {"entity": "certificates", "verb": "all", "value_field": "certificateId"},
    "sshKeyId": {"entity": "sshKey", "verb": "all", "value_field": "sshKeyId"},
    "customGitSSHKeyId": {"entity": "sshKey", "verb": "all", "value_field": "sshKeyId"},
    "githubId": {
        "entity": "gitProvider",
        "verb": "getAll",
        "value_field": "github.githubId",
        "filter_field": "providerType",
        "filter_value": "github",
    },
    "gitlabId": {
        "entity": "gitProvider",
        "verb": "getAll",
        "value_field": "gitlab.gitlabId",
        "filter_field": "providerType",
        "filter_value": "gitlab",
    },
    "bitbucketId": {
        "entity": "gitProvider",
        "verb": "getAll",
        "value_field": "bitbucket.bitbucketId",
        "filter_field": "providerType",
        "filter_value": "bitbucket",
    },
    "giteaId": {
        "entity": "gitProvider",
        "verb": "getAll",
        "value_field": "gitea.giteaId",
        "filter_field": "providerType",
        "filter_value": "gitea",
    },
    "gitProviderId": {"entity": "gitProvider", "verb": "getAll", "value_field": "gitProviderId"},
    "environmentId": {
        "entity": "environment",
        "verb": "byProjectId",
        "value_field": "environmentId",
        # ``params`` map query params to context keys; the form resolves them
        # from its navigation context (e.g. the current project) before fetching.
        "params": {"projectId": "projectId"},
    },
    # Service/db parents: enumerated across the project tree (no list endpoint).
    "composeId": {"service": "compose", "value_field": "composeId"},
    "applicationId": {"service": "application", "value_field": "applicationId"},
    "postgresId": {"service": "postgres", "value_field": "postgresId"},
    "mysqlId": {"service": "mysql", "value_field": "mysqlId"},
    "mariadbId": {"service": "mariadb", "value_field": "mariadbId"},
    "mongoId": {"service": "mongo", "value_field": "mongoId"},
    "redisId": {"service": "redis", "value_field": "redisId"},
    "libsqlId": {"service": "libsql", "value_field": "libsqlId"},
}

# Nested environment array that holds each service kind (``project.one`` ->
# ``environments`` -> ``<key>``).
SERVICE_ARRAY_KEYS: dict[str, str] = {
    "compose": "compose",
    "application": "applications",
    "postgres": "postgres",
    "mysql": "mysql",
    "mariadb": "mariadb",
    "mongo": "mongo",
    "redis": "redis",
    "libsql": "libsql",
}


def fk_source(field_name: str) -> dict | None:
    """The source spec for an FK field, if curated."""
    return FK_SOURCES.get(field_name)


def fk_route(source: dict) -> str:
    """The list route that enumerates the source's candidates."""
    return f"{source['entity']}.{source['verb']}"


def load_fk_candidates(
    connection: ConnectionConfig,
    source: dict,
    params: dict | None = None,
    cache: dict | None = None,
) -> list[dict]:
    """Fetch the candidates of an FK source as a list of records.

    ``params`` are extra query params (e.g. ``projectId`` for
    ``environment.byProjectId``); ``cache`` (a dict) memoizes the expensive
    service-tree enumeration. Runs off the event loop (the caller wraps it in
    ``asyncio.to_thread``). Raises :class:`httpx.HTTPError` when the source is
    unreachable or a required param is missing.
    """
    if source.get("service"):
        return _load_service_candidates(connection, source["service"], cache)
    response = APIClient(connection).request("GET", fk_route(source), params or {})
    data = response.json()
    records = data if isinstance(data, list) else data.get("items", [])
    records = [item for item in records if isinstance(item, dict)]
    filter_field = source.get("filter_field")
    filter_value = source.get("filter_value")
    if filter_field:
        records = [item for item in records if item.get(filter_field) == filter_value]
    return records


def _load_service_candidates(
    connection: ConnectionConfig, service_kind: str, cache: dict | None = None
) -> list[dict]:
    """Enumerate every live ``service_kind`` service across the project tree.

    There is no per-kind list endpoint, so the tree is walked via
    ``project.all`` → ``project.one`` → ``environments`` → ``<kind>``. The walk
    is memoized in ``cache`` keyed by (connection, kind).
    """
    key = ("service", connection.name, service_kind)
    if cache is not None and key in cache:
        return cache[key]
    client = APIClient(connection)
    records: list[dict] = []
    try:
        projects = client.request("GET", "project.all", {}).json()
    except httpx.HTTPError:
        projects = []
    array_key = SERVICE_ARRAY_KEYS[service_kind]
    for project in projects or []:
        if not isinstance(project, dict) or not project.get("projectId"):
            continue
        try:
            one = client.request("GET", "project.one", {"projectId": project["projectId"]}).json()
        except httpx.HTTPError:
            continue
        for environment in one.get("environments") or []:
            if not isinstance(environment, dict):
                continue
            records.extend(item for item in environment.get(array_key) or [] if isinstance(item, dict))
    if cache is not None:
        cache[key] = records
    return records


def _record_value(record: dict, path: str):
    """Resolve a (possibly dotted) field path in a record, e.g. ``github.githubId``."""
    value = record
    for part in path.split("."):
        if not isinstance(value, dict):
            return None
        value = value.get(part)
    return value


def candidate_options(records: list[dict], source: dict) -> list[tuple[str, str]]:
    """Map candidate records to ``(label, id)`` options for the dropdown."""
    value_field = source["value_field"]
    options = []
    for record in records:
        value = _record_value(record, value_field)
        if value:
            options.append((record_title(record), str(value)))
    return options
