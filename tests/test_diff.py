"""Diff/plan tests."""

from dokli.diff import build_plan
from dokli.manifest import Manifest
from dokli.state import LiveEnvironment, LiveGitProvider, LiveProject, LiveService, State


def _state(
    projects: list[LiveProject] | None = None,
    providers: list[LiveGitProvider] | None = None,
) -> State:
    return State(connection="test-env", projects=projects or [], git_providers=providers or [], servers=[])


def _compose_live(name: str, service_id: str, **overrides) -> LiveService:
    defaults = {
        "service_id": service_id,
        "app_name": name,
        "type": "compose",
        "name": name,
        "source_type": "raw",
        "compose_file": "version: '3'",
        "compose_path": "docker-compose.yml",
    }
    defaults.update(overrides)
    return LiveService(**defaults)


def _project_live(name: str, services: list[LiveService]) -> LiveProject:
    return LiveProject(
        project_id=name,
        name=name,
        environments=[
            LiveEnvironment(
                environment_id="e1",
                name="production",
                is_default=True,
                services=services,
            )
        ],
    )


class TestBuildPlan:
    """Plan building tests."""

    def test_project_to_create(self):
        """We expect a plan with creates when the project is missing."""
        manifest = Manifest.model_validate(
            {
                "connection": "test-env",
                "projects": [{"name": "new-app", "services": [{"type": "compose", "name": "backend"}]}],
            }
        )
        plan = build_plan(manifest, _state(projects=[]))

        actions = [item.action for item in plan.items]
        assert actions == ["create", "create"]
        assert plan.items[0].kind == "project"
        assert plan.items[1].kind == "compose"

    def test_service_to_create(self):
        """We expect a create when the service is missing in an existing project."""
        manifest = Manifest.model_validate(
            {"connection": "test-env", "projects": [{"name": "app", "services": [{"type": "compose", "name": "new"}]}]}
        )
        state = _state(projects=[_project_live("app", [_compose_live("existing", "s1")])])

        plan = build_plan(manifest, state)

        assert plan.has_changes
        assert plan.items[0].action == "create"
        assert plan.items[0].name == "new"

    def test_no_changes(self):
        """We expect an empty plan when manifest matches the live state."""
        manifest = Manifest.model_validate(
            {
                "connection": "test-env",
                "projects": [
                    {
                        "name": "app",
                        "services": [
                            {"type": "compose", "name": "backend", "compose_file": "version: '3'"},
                        ],
                    }
                ],
            }
        )
        state = _state(projects=[_project_live("app", [_compose_live("backend", "s1")])])

        plan = build_plan(manifest, state)

        assert not plan.has_changes

    def test_service_update_changes(self):
        """We expect an update with the changed fields listed."""
        manifest = Manifest.model_validate(
            {
                "connection": "test-env",
                "projects": [
                    {
                        "name": "app",
                        "services": [{"type": "compose", "name": "backend", "compose_file": "version: '3.8'"}],
                    }
                ],
            }
        )
        state = _state(projects=[_project_live("app", [_compose_live("backend", "s1")])])

        plan = build_plan(manifest, state)

        assert plan.items[0].action == "update"
        assert plan.items[0].changed == ["compose_file"]

    def test_git_provider_missing(self):
        """We expect a validate item when a git provider is missing."""
        manifest = Manifest.model_validate(
            {
                "connection": "test-env",
                "git_providers": [{"name": "github-main", "provider": "github"}],
            }
        )
        plan = build_plan(manifest, _state(providers=[]))

        assert plan.items[0].action == "validate"
        assert plan.items[0].kind == "git_provider"

    def test_git_provider_not_configured(self):
        """We expect a validate item when a git provider is not configured."""
        manifest = Manifest.model_validate(
            {
                "connection": "test-env",
                "git_providers": [{"name": "github-main", "provider": "github"}],
            }
        )
        provider = LiveGitProvider(
            git_provider_id="gp1",
            name="github-main",
            provider="github",
            is_configured=False,
        )
        plan = build_plan(manifest, _state(providers=[provider]))

        assert plan.items[0].action == "validate"
        assert "not configured" in plan.items[0].reason

    def test_git_provider_type_mismatch(self):
        """We expect a validate item when provider types differ."""
        manifest = Manifest.model_validate(
            {
                "connection": "test-env",
                "git_providers": [{"name": "github-main", "provider": "github"}],
            }
        )
        provider = LiveGitProvider(
            git_provider_id="gp1",
            name="github-main",
            provider="gitlab",
            is_configured=True,
        )
        plan = build_plan(manifest, _state(providers=[provider]))

        assert plan.items[0].action == "validate"
        assert "type mismatch" in plan.items[0].reason

    def test_database_service_changes(self):
        """We expect a database service diff to detect field changes."""
        manifest = Manifest.model_validate(
            {
                "connection": "test-env",
                "projects": [
                    {
                        "name": "app",
                        "services": [
                            {
                                "type": "postgres",
                                "name": "db",
                                "database_name": "newdb",
                                "database_user": "app",
                            }
                        ],
                    }
                ],
            }
        )
        live = _compose_live("db", "pg1", type="postgres", database_name="olddb", database_user="app")
        state = _state(projects=[_project_live("app", [live])])

        plan = build_plan(manifest, state)

        assert plan.items[0].action == "update"
        assert "database_name" in plan.items[0].changed
        assert "database_user" not in plan.items[0].changed

    def test_missing_environment_to_create(self):
        """We expect a plan with creates for a missing named environment."""
        manifest = Manifest.model_validate(
            {
                "connection": "test-env",
                "projects": [
                    {
                        "name": "app",
                        "environments": [
                            {
                                "name": "staging",
                                "services": [{"type": "compose", "name": "api", "compose_file": "x: 1"}],
                            }
                        ],
                    }
                ],
            }
        )
        state = _state(projects=[_project_live("app", [])])

        plan = build_plan(manifest, state)

        assert plan.items[0].action == "create"
        assert plan.items[0].kind == "environment"
        assert plan.items[0].name == "staging"
        assert plan.items[1].kind == "compose"
        assert plan.items[1].name == "api"

    def test_existing_environment_service_change(self):
        """We expect an update for a service inside an existing environment."""
        manifest = Manifest.model_validate(
            {
                "connection": "test-env",
                "projects": [
                    {
                        "name": "app",
                        "environments": [
                            {
                                "name": "staging",
                                "services": [{"type": "compose", "name": "api", "compose_file": "version: '3.8'"}],
                            }
                        ],
                    }
                ],
            }
        )
        staging = LiveEnvironment(
            environment_id="e-staging",
            name="staging",
            is_default=False,
            services=[_compose_live("api", "s2")],
        )
        state = _state(
            projects=[
                LiveProject(
                    project_id="app",
                    name="app",
                    environments=[staging],
                )
            ]
        )

        plan = build_plan(manifest, state)

        assert plan.items[0].action == "update"
        assert plan.items[0].name == "api"
        assert plan.items[0].changed == ["compose_file"]
