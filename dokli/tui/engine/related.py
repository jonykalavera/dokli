"""Related entities and parameter sources.

Some actions take required parameters that reference a *related* entity rather
than a field on the record itself. For example ``compose.readLogs`` needs a
``containerId`` (a docker container), which is not part of the compose record
but can be enumerated via ``docker.getContainersByAppNameMatch(appName)``. The
OpenAPI document does not express these relations, so they are declared here.
"""

import httpx

from dokli.tui.engine.introspect import record_id
from dokli.tui.engine.spec import EntityRegistry

# Parent entity -> provider spec that enumerates its related records.
#   entity: provider entity (e.g. docker), verb: action to call,
#   fill: {provider param: record field}, label: section title in the UI.
# The ``appName`` param is the docker *project* name: ``compose.one`` exposes it
# as ``appName`` (a slug like ``media-torrents-92opw6``), which is what the
# containers endpoint matches against. Composes also need ``appType`` from their
# ``composeType``. List-level records lack these fields, so ``related_records``
# enriches them via the entity's ``one`` action first.
RELATED_PROVIDERS: dict[str, dict] = {
    "compose": {
        "entity": "docker",
        "verb": "getContainersByAppNameMatch",
        "stack_verb": "getStackContainersByAppName",
        "fill": {"appName": "appName", "appType": "composeType", "serverId": "serverId"},
        "label": "Containers",
    },
    "application": {
        "entity": "docker",
        "verb": "getContainersByAppNameMatch",
        "fill": {"appName": "appName", "serverId": "serverId"},
        "label": "Containers",
    },
    "postgres": {
        "entity": "docker",
        "verb": "getContainersByAppNameMatch",
        "fill": {"appName": "appName", "serverId": "serverId"},
        "label": "Containers",
    },
    "mysql": {
        "entity": "docker",
        "verb": "getContainersByAppNameMatch",
        "fill": {"appName": "appName", "serverId": "serverId"},
        "label": "Containers",
    },
    "mariadb": {
        "entity": "docker",
        "verb": "getContainersByAppNameMatch",
        "fill": {"appName": "appName", "serverId": "serverId"},
        "label": "Containers",
    },
    "mongo": {
        "entity": "docker",
        "verb": "getContainersByAppNameMatch",
        "fill": {"appName": "appName", "serverId": "serverId"},
        "label": "Containers",
    },
    "redis": {
        "entity": "docker",
        "verb": "getContainersByAppNameMatch",
        "fill": {"appName": "appName", "serverId": "serverId"},
        "label": "Containers",
    },
    "libsql": {
        "entity": "docker",
        "verb": "getContainersByAppNameMatch",
        "fill": {"appName": "appName", "serverId": "serverId"},
        "label": "Containers",
    },
}

# Missing required param -> how to fill it from the related records of the
# current parent entity. value_field is the candidate's id, label_field the
# field shown in the picker.
PARAM_SOURCES: dict[str, dict] = {
    "containerId": {"value_field": "containerId", "label_field": "name"},
}

# Contextual related-entity list actions, surfaced as a separate action on the
# parent record. The schema does not express these relations (e.g. a compose's
# deployments), so they are declared here.
#   entity: related entity, verb: action to call, fill: {param: record field},
#   label: section/action title in the UI.
RELATED_ACTIONS: dict[str, list[dict]] = {
    "compose": [
        {
            "entity": "deployment",
            "verb": "allByCompose",
            "fill": {"composeId": "composeId"},
            "label": "Deployments",
            "key": "d",
        },
    ],
    "application": [
        {
            "entity": "deployment",
            "verb": "all",
            "fill": {"applicationId": "applicationId"},
            "label": "Deployments",
            "key": "d",
        },
    ],
    "server": [
        {
            "entity": "deployment",
            "verb": "allByServer",
            "fill": {"serverId": "serverId"},
            "label": "Deployments",
            "key": "d",
        },
    ],
}

# Entities whose ``all`` requires a parent id: the canonical no-param list
# action used when listing them at the top level.
LIST_VERB_OVERRIDES: dict[str, str] = {
    "deployment": "allCentralized",
}

# Actions of the parent service exposed on a child record (e.g. a docker
# container's logs via the parent service's readLogs). ``fill`` maps params
# taken from the child record; the parent's own id comes from the parent record.
#   verb: parent action verb, fill: {param: child field}, label, key.
PARENT_ACTIONS: dict[str, list[dict]] = {
    "docker": [
        {"verb": "readLogs", "fill": {"containerId": "containerId"}, "label": "Logs", "key": "L"},
    ],
}


def parent_action_spec(entity: str, route: str) -> dict | None:
    """The PARENT_ACTIONS spec whose parent action route matches ``route``, if any."""
    for spec in PARENT_ACTIONS.get(entity, []):
        if spec["verb"] == route.split(".", 1)[-1]:
            return spec
    return None


def related_spec(parent_entity: str) -> dict | None:
    """The related-provider spec for a parent entity, if any."""
    return RELATED_PROVIDERS.get(parent_entity)


def related_action_spec(parent_entity: str, route: str) -> dict | None:
    """The RELATED_ACTIONS spec whose entity.verb matches ``route``, if any."""
    for spec in RELATED_ACTIONS.get(parent_entity, []):
        if f"{spec['entity']}.{spec['verb']}" == route:
            return spec
    return None


def list_verb_override(entity: str) -> str | None:
    """The canonical no-param list verb for an entity, if its ``all`` needs a parent."""
    return LIST_VERB_OVERRIDES.get(entity)


def param_source(param: str) -> dict | None:
    """The source spec able to fill a missing required param, if any."""
    return PARAM_SOURCES.get(param)


def related_records(client, registry: EntityRegistry, parent_entity: str, record: dict) -> list[dict]:
    """Fetch the related records of a parent record.

    The record is enriched via the entity's ``one`` action when it lacks the
    fields the provider needs (e.g. the docker project ``appName``). Returns a
    list of records (each carrying its own id field), or ``[]`` when the entity
    has no provider or the lookup fails.
    """
    spec = RELATED_PROVIDERS.get(parent_entity)
    if spec is None:
        return []
    record = _enrich_record(client, registry, parent_entity, record, spec["fill"])
    # Stack-type composes run on swarm: their containers come from a different
    # endpoint that takes no ``appType``.
    if spec.get("stack_verb") and record.get("composeType") == "stack":
        verb = spec["stack_verb"]
        fill = {key: value for key, value in spec["fill"].items() if key != "appType"}
    else:
        verb = spec["verb"]
        fill = spec["fill"]
    entity = registry.get(spec["entity"])
    action = entity.get(verb) if entity else None
    if action is None:
        return []
    params = _build_params(record, fill)
    if not params:
        return []
    try:
        data = client.request("GET", action.route, params).json()
    except httpx.HTTPError:
        return []
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    items = data.get("items", []) if isinstance(data, dict) else []
    return [item for item in items if isinstance(item, dict)]


def _build_params(record: dict, fill: dict) -> dict:
    """Fill provider params from the record, falling back ``appName`` to ``name``."""
    params = {}
    for param, field in fill.items():
        value = record.get(field)
        if not value and param == "appName":
            value = record.get("name")
        if value:
            params[param] = value
    return params


def _enrich_record(client, registry: EntityRegistry, parent_entity: str, record: dict, fill: dict) -> dict:
    """Merge in the entity's ``one`` record when fill fields are missing."""
    for field in fill.values():
        if record.get(field):
            continue
        entity = registry.get(parent_entity)
        one = entity.get("one") if entity else None
        if one is None:
            return record
        params = {}
        for param in one.param_names:
            value = record.get(param) or record_id(record, parent_entity)
            if value:
                params[param] = value
        if not params:
            return record
        try:
            enriched = client.request("GET", one.route, params).json()
        except httpx.HTTPError:
            return record
        if isinstance(enriched, dict):
            return {**record, **enriched}
        return record
    return record
