"""Related entities and parameter sources.

Some actions take required parameters that reference a *related* entity rather
than a field on the record itself. For example ``compose.readLogs`` needs a
``containerId`` (a docker container), which is not part of the compose record
but can be enumerated via ``docker.getContainersByAppNameMatch(appName)``. The
OpenAPI document does not express these relations, so they are declared here.
"""

import httpx

from dokli.tui.engine.spec import EntityRegistry

# Parent entity -> provider spec that enumerates its related records.
#   entity: provider entity (e.g. docker), verb: action to call,
#   fill: {provider param: record field}, label: section title in the UI.
RELATED_PROVIDERS: dict[str, dict] = {
    "compose": {
        "entity": "docker",
        "verb": "getContainersByAppNameMatch",
        "fill": {"appName": "name", "serverId": "serverId"},
        "label": "Containers",
    },
    "application": {
        "entity": "docker",
        "verb": "getContainersByAppNameMatch",
        "fill": {"appName": "name", "serverId": "serverId"},
        "label": "Containers",
    },
    "postgres": {
        "entity": "docker",
        "verb": "getContainersByAppNameMatch",
        "fill": {"appName": "name", "serverId": "serverId"},
        "label": "Containers",
    },
    "mysql": {
        "entity": "docker",
        "verb": "getContainersByAppNameMatch",
        "fill": {"appName": "name", "serverId": "serverId"},
        "label": "Containers",
    },
    "mariadb": {
        "entity": "docker",
        "verb": "getContainersByAppNameMatch",
        "fill": {"appName": "name", "serverId": "serverId"},
        "label": "Containers",
    },
    "mongo": {
        "entity": "docker",
        "verb": "getContainersByAppNameMatch",
        "fill": {"appName": "name", "serverId": "serverId"},
        "label": "Containers",
    },
    "redis": {
        "entity": "docker",
        "verb": "getContainersByAppNameMatch",
        "fill": {"appName": "name", "serverId": "serverId"},
        "label": "Containers",
    },
    "libsql": {
        "entity": "docker",
        "verb": "getContainersByAppNameMatch",
        "fill": {"appName": "name", "serverId": "serverId"},
        "label": "Containers",
    },
}

# Missing required param -> how to fill it from the related records of the
# current parent entity. value_field is the candidate's id, label_field the
# field shown in the picker.
PARAM_SOURCES: dict[str, dict] = {
    "containerId": {"value_field": "containerId", "label_field": "name"},
}


def related_spec(parent_entity: str) -> dict | None:
    """The related-provider spec for a parent entity, if any."""
    return RELATED_PROVIDERS.get(parent_entity)


def param_source(param: str) -> dict | None:
    """The source spec able to fill a missing required param, if any."""
    return PARAM_SOURCES.get(param)


def related_records(client, registry: EntityRegistry, parent_entity: str, record: dict) -> list[dict]:
    """Fetch the related records of a parent record.

    Returns a list of records (each carrying its own id field), or ``[]`` when
    the entity has no provider or the lookup fails.
    """
    spec = RELATED_PROVIDERS.get(parent_entity)
    if spec is None:
        return []
    entity = registry.get(spec["entity"])
    action = entity.get(spec["verb"]) if entity else None
    if action is None:
        return []
    params = {param: record[field] for param, field in spec["fill"].items() if record.get(field)}
    try:
        data = client.request("GET", action.route, params).json()
    except httpx.HTTPError:
        return []
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    items = data.get("items", []) if isinstance(data, dict) else []
    return [item for item in items if isinstance(item, dict)]
