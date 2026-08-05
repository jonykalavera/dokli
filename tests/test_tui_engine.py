"""TUI engine tests (spec parsing, schemas, introspection)."""

from pydantic import SecretStr

from dokli.tui.engine import (
    Entity,
    EntityAction,
    EntityRegistry,
    action_bindings,
    build_form_model,
    classify,
    entity_icon,
    field_label,
    icon_label,
    infer_columns,
    key_for_verb,
    nested_child_entity,
    parse_spec,
    record_id,
    record_title,
    state_color,
    state_indicator,
)


def _spec() -> dict:
    return {
        "paths": {
            "/project.all": {"get": {"summary": "List projects"}},
            "/project.one": {"get": {"parameters": [{"name": "projectId", "in": "query", "required": True}]}},
            "/project.create": {
                "post": {
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "description": {"type": "string"},
                                    },
                                    "required": ["name"],
                                }
                            }
                        }
                    }
                }
            },
            "/project.remove": {"post": {}},
            "/environment.create": {
                "post": {
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "projectId": {"type": "string"},
                                        "name": {"type": "string"},
                                    },
                                    "required": ["name", "projectId"],
                                }
                            }
                        }
                    }
                }
            },
            "/compose.create": {
                "post": {
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "environmentId": {"type": "string"},
                                        "serverId": {"type": "string"},
                                        "name": {"type": "string"},
                                    },
                                    "required": ["name", "environmentId"],
                                }
                            }
                        }
                    }
                }
            },
            "/compose.deploy": {"post": {}},
        }
    }


class TestParseSpec:
    """Spec parsing tests."""

    def test_parses_entities_and_actions(self):
        """We expect entities and actions to be discovered."""
        registry = parse_spec(_spec())
        assert isinstance(registry, EntityRegistry)
        assert "project" in registry.names()
        assert "compose" in registry.names()
        assert "environment" in registry.names()
        project = registry.get("project")
        assert isinstance(project, Entity)
        assert set(project.actions) == {"all", "one", "create", "remove"}

    def test_listable(self):
        """We expect entities with an all action to be listable."""
        registry = parse_spec(_spec())
        assert registry.listable() == ["project"]
        assert registry.get("compose").listable is False

    def test_parent_entity_inference(self):
        """We expect the parent to be inferred from create foreign keys."""
        registry = parse_spec(_spec())
        assert registry.get("environment").parent_entity == "project"
        assert registry.get("compose").parent_entity == "environment"
        assert registry.get("project").parent_entity is None

    def test_navigation_path(self):
        """We expect the ancestor chain to be computed."""
        registry = parse_spec(_spec())
        assert registry.navigation_path("compose") == ["project", "environment", "compose"]
        assert registry.navigation_path("project") == ["project"]

    def test_nested_child_entity(self):
        """We expect nested array keys to map to child entities."""
        assert nested_child_entity("environments") == "environment"
        assert nested_child_entity("compose") == "compose"
        assert nested_child_entity("unknown") is None

    def test_action_details(self):
        """We expect action metadata to be extracted."""
        registry = parse_spec(_spec())
        create = registry.get("project").get("create")
        assert isinstance(create, EntityAction)
        assert create.method == "POST"
        assert create.route == "project.create"
        assert create.request_schema["required"] == ["name"]
        one = registry.get("project").get("one")
        assert one.param_names == ["projectId"]


class TestClassify:
    """Verb classification tests."""

    def _action(self, verb: str, method: str = "GET") -> EntityAction:
        return EntityAction(verb=verb, method=method, route=f"x.{verb}")

    def test_classification(self):
        """We expect verbs to map to generic interactions."""
        assert classify(self._action("all")) == "list"
        assert classify(self._action("one")) == "detail"
        assert classify(self._action("create", "POST")) == "form"
        assert classify(self._action("update", "POST")) == "form"
        assert classify(self._action("saveEnvironment", "POST")) == "form"
        assert classify(self._action("remove", "POST")) == "action"
        assert classify(self._action("deploy", "POST")) == "action"


class TestKeyBindings:
    """Keybinding assignment tests."""

    def _entity(self, *verbs: str) -> Entity:
        actions = {verb: EntityAction(verb=verb, method="POST", route=f"x.{verb}") for verb in verbs}
        return Entity(name="x", actions=actions)

    def test_update_uses_u(self):
        """We expect update to be bound to its first letter."""
        assert key_for_verb("update") == "u"

    def test_respects_display_order(self):
        """We expect keys to follow display order, earlier actions winning collisions."""
        entity = self._entity("create", "update", "remove")
        bindings = action_bindings(entity)
        by_verb = {action.verb: key for action, key in bindings}
        assert by_verb["create"] == "c"
        assert by_verb["update"] == "u"
        assert by_verb["remove"] == "d"

    def test_collision_resolved_by_order(self):
        """We expect the first action to keep its preferred key on a collision."""
        entity = self._entity("remove", "redeploy", "restart")
        bindings = action_bindings(entity)
        by_verb = {action.verb: key for action, key in bindings}
        assert by_verb["remove"] == "d"
        assert by_verb["restart"] == "R"

    def test_fallback_to_free_key(self):
        """We expect a free key when all verb letters are taken."""
        assert key_for_verb("xyz", frozenset("xyzw")) == "a"

    def test_all_actions_get_keys(self):
        """We expect every action to receive a key, even with many actions."""
        entity = self._entity(
            "remove",
            "redeploy",
            "restart",
            "search",
            "start",
            "save",
            "suggest",
            "sync",
            "show",
            "stop",
            "status",
            "submit",
        )
        bindings = action_bindings(entity)
        assert all(key is not None for _, key in bindings)


class TestIcons:
    """Entity icon tests."""

    def test_known_entities_have_icons(self):
        """We expect known entities to map to an icon."""
        assert entity_icon("project") != ""
        assert entity_icon("postgres") != ""
        assert entity_icon("redis") != ""

    def test_fallback_for_unknown(self):
        """We expect unknown entities to get a fallback icon."""
        assert entity_icon("totally_unknown") == "\uf15b"

    def test_icon_label_wraps_in_color(self):
        """We expect icon_label to put the icon in a colored box."""
        label = icon_label("project")
        assert "on yellow" in label
        assert "\uf07b" in label
        fallback = icon_label("totally_unknown")
        assert "on grey70" in fallback

    def test_state_color(self):
        """We expect a traffic-light color per container state."""
        assert state_color("running") == "green"
        assert state_color("paused") == "yellow"
        assert state_color("restarting") == "yellow"
        assert state_color("exited") == "red"
        assert state_color("") == "grey70"

    def test_state_indicator(self):
        """We expect a colored dot for the container state."""
        assert state_indicator("running") == "[bold green]●[/]"
        assert state_indicator("exited") == "[bold red]●[/]"


class TestBuildFormModel:
    """Schema → form model tests."""

    def test_model_fields(self):
        """We expect a model with the schema's fields."""
        model = build_form_model(
            {
                "properties": {"name": {"type": "string"}, "count": {"type": "integer"}},
                "required": ["name"],
            }
        )
        instance = model(name="x", count=3)
        assert instance.name == "x"
        assert instance.count == 3

    def test_secret_fields(self):
        """We expect secret-like fields to be SecretStr."""
        model = build_form_model({"properties": {"databasePassword": {"type": "string"}}})
        instance = model(databasePassword="hunter2")
        assert isinstance(instance.databasePassword, SecretStr)

    def test_enum_fields(self):
        """We expect string enums to be Literal."""
        model = build_form_model({"properties": {"mode": {"type": "string", "enum": ["dev", "prod"]}}})
        assert model(mode="dev").mode == "dev"

    def test_anyof_annotation(self):
        """We expect anyOf null-unions to be unwrapped."""
        model = build_form_model({"properties": {"autoDeploy": {"anyOf": [{"type": "boolean"}, {"type": "null"}]}}})
        assert model(autoDeploy=True).autoDeploy is True

    def test_filters_read_only_fields(self):
        """We expect server-managed fields to be filtered from the form."""
        model = build_form_model(
            {
                "properties": {
                    "name": {"type": "string"},
                    "createdAt": {"type": "string"},
                    "organizationId": {"type": "string"},
                    "applicationStatus": {"type": "string"},
                }
            }
        )
        assert "name" in model.model_fields
        assert "createdAt" not in model.model_fields
        assert "organizationId" not in model.model_fields
        assert "applicationStatus" not in model.model_fields


class TestIntrospect:
    """Introspection helpers tests."""

    def test_field_label(self):
        """We expect camelCase to be turned into a title."""
        assert field_label("composeStatus") == "Compose Status"
        assert field_label("name") == "Name"

    def test_record_id(self):
        """We expect the entity-specific id to be found."""
        assert record_id({"projectId": "p1", "name": "x"}, "project") == "p1"
        assert record_id({"id": "p1"}) == "p1"

    def test_record_title(self):
        """We expect a sensible title for a record."""
        assert record_title({"name": "myapp"}) == "myapp"
        assert record_title({"projectId": "p1"}) == "p1"

    def test_infer_columns(self):
        """We expect preferred columns to be picked."""
        records = [{"projectId": "p1", "name": "x", "description": "d", "createdAt": "t", "env": ""}]
        columns = infer_columns(records, "project")
        assert "name" in columns
        assert "createdAt" not in columns
