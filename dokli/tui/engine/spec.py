"""OpenAPI document → entity registry."""

from pydantic import BaseModel, Field


class EntityAction(BaseModel):
    """An API action of an entity (e.g. ``project.create``)."""

    verb: str
    method: str
    route: str
    summary: str = ""
    request_schema: dict = Field(default_factory=dict)
    param_names: list[str] = Field(default_factory=list)

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


class EntityRegistry(BaseModel):
    """All entities discovered from an OpenAPI document."""

    entities: dict[str, Entity] = Field(default_factory=dict)

    def names(self) -> list[str]:
        """Sorted entity names."""
        return sorted(self.entities)

    def get(self, name: str) -> Entity | None:
        """Get an entity by name."""
        return self.entities.get(name)


LIST_VERBS = {"all"}
DETAIL_VERBS = {"one"}
DESTRUCTIVE_VERBS = {"remove", "delete"}
FORM_PREFIXES = ("create", "update", "save", "edit", "new")

CORE_ENTITIES = [
    "project",
    "compose",
    "application",
    "postgres",
    "mysql",
    "mariadb",
    "mongo",
    "redis",
    "libsql",
    "server",
    "domain",
    "deployment",
]


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


def parse_spec(schema: dict) -> EntityRegistry:
    """Build an entity registry from an OpenAPI document."""
    registry = EntityRegistry()
    for path, methods in schema.get("paths", {}).items():
        route = path.strip("/")
        if "." not in route:
            continue
        entity_name, _, verb = route.partition(".")
        for method, details in methods.items():
            action = EntityAction(
                verb=verb,
                method=method.upper(),
                route=route,
                summary=(details.get("summary") or details.get("description") or "").strip(),
                request_schema=_extract_request_schema(details),
                param_names=[parameter["name"] for parameter in details.get("parameters", [])],
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
