"""OpenAPI document → entity registry."""

import string

from pydantic import BaseModel, Field


class EntityAction(BaseModel):
    """An API action of an entity (e.g. ``project.create``)."""

    verb: str
    method: str
    route: str
    summary: str = ""
    request_schema: dict = Field(default_factory=dict)
    param_names: list[str] = Field(default_factory=list)
    required_params: list[str] = Field(default_factory=list)

    @property
    def label(self) -> str:
        """A human-friendly label for the action."""
        return f"{self.verb} ({self.method})"


class Entity(BaseModel):
    """An API entity with its actions."""

    name: str
    actions: dict[str, EntityAction] = Field(default_factory=dict)

    def get(self, verb: str) -> EntityAction | None:
        """Get an action by verb."""
        return self.actions.get(verb)

    @property
    def listable(self) -> bool:
        """Whether the entity has an ``all`` action (top-level listable)."""
        return "all" in self.actions

    @property
    def parent_entity(self) -> str | None:
        """The parent entity, inferred from foreign keys in the create schema.

        A required (or present) ``<parent>Id`` field in the request body (other
        than the entity's own id and ``serverId`` placement) points to its
        parent. E.g. ``compose.create`` requires ``environmentId``.
        """
        create = self.actions.get("create")
        if create is None:
            return None
        schema = create.request_schema
        fields = list(schema.get("required", [])) + list(schema.get("properties", {}))
        for field in fields:
            if not field.endswith("Id"):
                continue
            if field in (f"{self.name}Id", "serverId"):
                continue
            return field[:-2]
        return None


class EntityRegistry(BaseModel):
    """All entities discovered from an OpenAPI document."""

    entities: dict[str, Entity] = Field(default_factory=dict)

    def names(self) -> list[str]:
        """Sorted entity names."""
        return sorted(self.entities)

    def get(self, name: str) -> Entity | None:
        """Get an entity by name."""
        return self.entities.get(name)

    def listable(self) -> list[str]:
        """Entities that can be listed at the top level (have ``all``)."""
        return sorted(name for name, entity in self.entities.items() if entity.listable)

    def navigation_path(self, name: str) -> list[str]:
        """Chain of ancestors from a top-level entity down to ``name``."""
        path = [name]
        seen = {name}
        current = name
        while True:
            entity = self.get(current)
            parent = entity.parent_entity if entity else None
            if not parent or parent in seen or parent not in self.entities:
                break
            path.append(parent)
            seen.add(parent)
            current = parent
        return list(reversed(path))


LIST_VERBS = {"all"}
DETAIL_VERBS = {"one"}
DESTRUCTIVE_VERBS = {"remove", "delete"}
FORM_PREFIXES = ("create", "update", "save", "edit", "new")

# Response keys (nested arrays) → child entity name.
NESTED_CHILD_KEYS = {
    "environments": "environment",
    "applications": "application",
    "compose": "compose",
    "postgres": "postgres",
    "mysql": "mysql",
    "mariadb": "mariadb",
    "mongo": "mongo",
    "redis": "redis",
    "libsql": "libsql",
    "domains": "domain",
    "ports": "port",
    "mounts": "mount",
    "backups": "backup",
    "schedules": "schedule",
    "security": "security",
    "redirects": "redirects",
    "patches": "patch",
    "previewDeployments": "previewDeployment",
}


def nested_child_entity(key: str) -> str | None:
    """Map a nested response array key to its child entity, if known."""
    return NESTED_CHILD_KEYS.get(key)


def classify(action: EntityAction) -> str:
    """Classify an action into a generic interaction type."""
    if action.verb in LIST_VERBS:
        return "list"
    if action.verb in DETAIL_VERBS:
        return "detail"
    if action.verb in DESTRUCTIVE_VERBS:
        return "action"
    if action.verb.startswith(FORM_PREFIXES):
        return "form"
    return "action"


# Keys used by the browser navigation; never assigned to actions.
RESERVED_KEYS = frozenset("hjklrq")

# Fallback key space, in priority order: letters, then digits, then uppercase.
FALLBACK_KEYS = string.ascii_lowercase + string.digits + string.ascii_uppercase

VERB_KEYS = {
    "create": "c",
    "new": "c",
    "update": "u",
    "edit": "e",
    "save": "s",
    "remove": "d",
    "delete": "d",
    "deploy": "x",
    "redeploy": "X",
    "testConnection": "t",
    "restart": "R",
    "readLogs": "l",
}


def key_for_verb(verb: str, taken: frozenset[str] = frozenset()) -> str | None:
    """Assign a deterministic, collision-free keybinding to an action verb.

    Prefers the verb's own letters (``VERB_KEYS`` first), then any free letter
    of the alphabet, so every action can get a key.
    """
    if verb in VERB_KEYS and VERB_KEYS[verb] not in taken:
        return VERB_KEYS[verb]
    for character in verb:
        if character.isalpha() and character.lower() not in taken and character.lower() not in RESERVED_KEYS:
            return character.lower()
    for character in FALLBACK_KEYS:
        if character not in taken and character not in RESERVED_KEYS:
            return character
    return None


def action_bindings(entity: Entity) -> list[tuple[EntityAction, str | None]]:
    """Assign keybindings to an entity's actions.

    Keys are assigned in **display order** (the order actions appear in the
    spec): each action gets its preferred key (``VERB_KEYS``, else the first
    available letter of the verb), and earlier actions win key collisions.
    """
    taken: set[str] = set()
    bindings = []
    for action in entity.actions.values():
        if classify(action) in ("list", "detail"):
            continue
        key = key_for_verb(action.verb, frozenset(taken))
        if key:
            taken.add(key)
        bindings.append((action, key))
    return bindings


def parse_spec(schema: dict) -> EntityRegistry:
    """Build an entity registry from an OpenAPI document."""
    registry = EntityRegistry()
    for path, methods in schema.get("paths", {}).items():
        route = path.strip("/")
        if "." not in route:
            continue
        entity_name, _, verb = route.partition(".")
        for method, details in methods.items():
            parameters = details.get("parameters", [])
            action = EntityAction(
                verb=verb,
                method=method.upper(),
                route=route,
                summary=(details.get("summary") or details.get("description") or "").strip(),
                request_schema=_extract_request_schema(details),
                param_names=[parameter["name"] for parameter in parameters],
                required_params=[parameter["name"] for parameter in parameters if parameter.get("required")],
            )
            entity = registry.entities.setdefault(entity_name, Entity(name=entity_name))
            entity.actions[verb] = action
    return registry


def _extract_request_schema(details: dict) -> dict:
    body = details.get("requestBody", {})
    schema = body.get("content", {}).get("application/json", {}).get("schema", {})
    if schema.get("type") != "object":
        return {}
    return {
        "properties": schema.get("properties", {}),
        "required": schema.get("required", []),
    }
