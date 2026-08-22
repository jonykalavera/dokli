"""OpenAPI document → entity registry."""

from collections.abc import Iterable

from pydantic import BaseModel, Field

# Entities surfaced first in the top-level browser list; the rest follow
# alphabetically. Overridable via the TUI config's ``entity_order``.
PRIORITY_ENTITIES: tuple[str, ...] = ("project",)


def sort_entities(names: Iterable[str], priority: tuple[str, ...] = PRIORITY_ENTITIES) -> list[str]:
    """Sort entity names, honoring a priority prefix.

    Names in ``priority`` come first (in their given order); the rest follow
    alphabetically. Priority entries that are not present are ignored.
    """
    ordered = tuple(priority)
    return sorted(
        names,
        key=lambda name: (ordered.index(name) if name in ordered else len(ordered), name),
    )


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

    def listable(self, priority: tuple[str, ...] = PRIORITY_ENTITIES) -> list[str]:
        """Entities that can be listed at the top level (have ``all``).

        ``priority`` names come first (in order); the rest follow alphabetically.
        """
        return sort_entities(
            (name for name, entity in self.entities.items() if entity.listable),
            priority,
        )

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
RESERVED_KEYS = frozenset("hjklrqy")

# Keys reserved for app-level bindings (e.g. D toggles dark mode); never
# assigned to actions so the app shortcuts are not overshadowed.
SYSTEM_KEYS = frozenset("D")

# The curated set of frequent verbs that get a direct keybinding. Every other
# verb is reachable only through the command palette / action picker, so keys
# stay memorable and never change between versions. ``save`` uses ``w`` (write,
# vim-style) so ``s`` is free for the very common ``start``.
VERB_KEYS = {
    "create": "c",
    "new": "c",
    "update": "u",
    "edit": "e",
    "save": "w",
    "start": "s",
    "stop": "o",
    "remove": "delete",
    "delete": "delete",
    "deploy": "x",
    "redeploy": "X",
    "testConnection": "t",
    "restart": "R",
    "readLogs": "L",
    "rebuild": "b",
    "move": "m",
    "duplicate": "d",
    "rollback": "Z",
}


def key_for_verb(
    verb: str,
    taken: frozenset[str] = frozenset(),
    verb_keys: dict[str, str] | None = None,
    system_keys: frozenset[str] | None = None,
) -> str | None:
    """The curated key for an action verb, if it has one.

    Only verbs in ``verb_keys`` (the curated ``VERB_KEYS``, optionally extended
    via the user's TUI config) get a direct key; every other verb returns
    ``None`` and is reached only through the command palette / action picker.
    This keeps keys memorable and stable. ``verb_keys`` and ``system_keys``
    default to the module constants but can be overridden (e.g. from the user's
    TUI config).
    """
    verb_keys = verb_keys or VERB_KEYS
    system_keys = SYSTEM_KEYS if system_keys is None else system_keys
    if verb in verb_keys and verb_keys[verb] not in taken and verb_keys[verb] not in system_keys:
        return verb_keys[verb]
    return None


def action_bindings(
    entity: Entity,
    verb_keys: dict[str, str] | None = None,
    system_keys: frozenset[str] | None = None,
) -> list[tuple[EntityAction, str | None]]:
    """Assign keybindings to an entity's actions.

    Keys are assigned in **display order** (the order actions appear in the
    spec): each action gets its curated key (``VERB_KEYS``), and earlier
    actions win key collisions. Actions without a curated verb key get
    ``None`` (reachable via the command palette / action picker).
    """
    taken: set[str] = set()
    bindings = []
    for action in entity.actions.values():
        if classify(action) in ("list", "detail"):
            continue
        key = key_for_verb(action.verb, frozenset(taken), verb_keys, system_keys)
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
