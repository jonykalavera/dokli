"""Probe which entities are usable with the current API key.

Some Dokploy endpoints are gated behind an enterprise license or admin
permissions and return 401/403 even for an owner API key on a self-hosted
instance. Probing each listable entity's ``all`` action at runtime lets the TUI
hide the ones that cannot be used, regardless of the Dokploy version.
"""

import httpx

# Status codes that mean the endpoint is authorized. Because APIClient raises on
# non-2xx, only 2xx actually reach this check (a bare 204 still counts as usable).
USABLE_STATUS = range(200, 300)

_PROBE_CACHE: dict[str, dict[str, bool]] = {}


def probe_entity(client, entity) -> bool:
    """Return True if the entity's list action is usable (not 401/403).

    Only 401/403 mark an entity as unusable. Bad input (4xx), a missing
    resource (404) and transport errors (timeout, refused connection) leave it
    usable so a transient network blip does not hide the entity. An ``all``
    action that requires parameters (e.g. ``deployment.all`` needs an
    ``applicationId``) cannot be listed from the top level, so it counts as
    unusable too.
    """
    action = entity.get("all")
    if action is None:
        return True
    if action.required_params:
        return False
    try:
        response = client.request("GET", action.route, {})
        return response.status_code in USABLE_STATUS
    except httpx.HTTPStatusError as err:
        return err.response.status_code not in (401, 403)
    except httpx.HTTPError:
        return True


def probe_entities(client, registry, connection_name: str) -> dict[str, bool]:
    """Probe all listable entities of a connection, caching the results."""
    cached = _PROBE_CACHE.get(connection_name)
    if cached is not None:
        return cached
    results = {}
    for name in registry.listable():
        entity = registry.get(name)
        results[name] = probe_entity(client, entity) if entity else True
    _PROBE_CACHE[connection_name] = results
    return results


def clear_probe_cache(connection_name: str) -> None:
    """Drop the cached probe results for a connection."""
    _PROBE_CACHE.pop(connection_name, None)
