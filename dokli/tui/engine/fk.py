"""Foreign-key form controls: FK field -> candidate source.

Action forms show ``*Id`` fields as raw id inputs. For FK fields that reference
a listable entity (e.g. ``serverId`` → ``server.all``) the form renders a
dropdown of candidates instead, falling back to free text when the source is
unavailable. Sources are curated here because the OpenAPI document does not
express these relations.
"""

from dokli.api_client import APIClient
from dokli.config import ConnectionConfig
from dokli.tui.engine.introspect import record_title

# FK field name -> source spec. ``entity``+``verb`` form the list route (e.g.
# ``server.all``); ``value_field`` is the candidate's id key; ``filter_field``
# optionally narrows candidates (e.g. git providers by ``providerType``).
# Fields without a curated source fall back to a plain text input.
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
        "value_field": "gitProviderId",
        "filter_field": "providerType",
        "filter_value": "github",
    },
    "gitlabId": {
        "entity": "gitProvider",
        "verb": "getAll",
        "value_field": "gitProviderId",
        "filter_field": "providerType",
        "filter_value": "gitlab",
    },
    "bitbucketId": {
        "entity": "gitProvider",
        "verb": "getAll",
        "value_field": "gitProviderId",
        "filter_field": "providerType",
        "filter_value": "bitbucket",
    },
    "giteaId": {
        "entity": "gitProvider",
        "verb": "getAll",
        "value_field": "gitProviderId",
        "filter_field": "providerType",
        "filter_value": "gitea",
    },
    "gitProviderId": {"entity": "gitProvider", "verb": "getAll", "value_field": "gitProviderId"},
}


def fk_source(field_name: str) -> dict | None:
    """The source spec for an FK field, if curated."""
    return FK_SOURCES.get(field_name)


def fk_route(source: dict) -> str:
    """The list route that enumerates the source's candidates."""
    return f"{source['entity']}.{source['verb']}"


def load_fk_candidates(connection: ConnectionConfig, source: dict) -> list[dict]:
    """Fetch the candidates of an FK source as a list of records.

    Runs off the event loop (the caller wraps it in ``asyncio.to_thread``).
    Raises :class:`httpx.HTTPError` when the source is unreachable.
    """
    response = APIClient(connection).request("GET", fk_route(source), {})
    data = response.json()
    records = data if isinstance(data, list) else data.get("items", [])
    records = [item for item in records if isinstance(item, dict)]
    filter_field = source.get("filter_field")
    filter_value = source.get("filter_value")
    if filter_field:
        records = [item for item in records if item.get(filter_field) == filter_value]
    return records


def candidate_options(records: list[dict], source: dict) -> list[tuple[str, str]]:
    """Map candidate records to ``(label, id)`` options for the dropdown."""
    value_field = source["value_field"]
    options = []
    for record in records:
        value = record.get(value_field)
        if value:
            options.append((record_title(record), str(value)))
    return options
