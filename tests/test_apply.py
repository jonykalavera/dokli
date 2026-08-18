"""Apply engine tests."""

from dokli.apply import Applier
from dokli.config import ConnectionConfig
from dokli.manifest import Manifest
from dokli.state import LiveEnvironment, LiveGitProvider, LiveProject, LiveService, State


class FakeResponse:
    """Minimal httpx.Response stand-in for tests."""

    def __init__(self, data):
        """Initialize with the payload to return from json()."""
        self._data = data

    def json(self):
        """Return the canned payload."""
        return self._data


def _connection() -> ConnectionConfig:
    return ConnectionConfig(name="test-env", url="https://example.com", api_key_cmd="echo key")


def _compose_live(name: str, service_id: str, **overrides) -> LiveService:
    defaults = {
        "service_id": service_id,
        "app_name": name,
        "type": "compose",
        "name": name,
        "source_type": "raw",
        "compose_file": "version: '3'",
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


def _provider_live(name: str, provider: str, is_configured: bool = True, **ids) -> LiveGitProvider:
    defaults = {"git_provider_id": "gp1", "name": name, "provider": provider, "is_configured": is_configured}
    defaults.update(ids)
    return LiveGitProvider(**defaults)


def _applier(mocker, state: State, responses: dict | None = None):
    """Build an Applier with a mocked API client."""
    client = mocker.Mock()
    responses = responses or {}

    def fake_request(method, path, params):
        if path in responses:
            return FakeResponse(responses[path])
        if path == "project.create":
            return FakeResponse({"project": {"projectId": "p-new"}, "environment": {"environmentId": "e-new"}})
        if path == "compose.create":
            return FakeResponse({"composeId": "c-new"})
        if path == "application.create":
            return FakeResponse({"applicationId": "a-new"})
        if path == "environment.create":
            return FakeResponse({"environmentId": "env-staging"})
        for service_type in ("postgres", "mysql", "mariadb", "mongo", "redis"):
            if path == f"{service_type}.create":
                return FakeResponse({f"{service_type}Id": f"{service_type}-new"})
        return FakeResponse({})

    client.request.side_effect = fake_request
    mocker.patch("dokli.apply.APIClient", return_value=client)
    mocker.patch("dokli.apply.collect_state", return_value=state)
    return client


class TestApplyCreate:
    """Create flows."""

    def test_dry_run_does_not_mutate(self, mocker):
        """We expect dry-run to only record creates."""
        manifest = Manifest.model_validate(
            {
                "connection": "test-env",
                "projects": [{"name": "app", "services": [{"type": "compose", "name": "backend"}]}],
            }
        )
        client = _applier(mocker, State(connection="test-env"))

        report = Applier(manifest, _connection()).run(dry_run=True)

        client.request.assert_not_called()
        assert [a.action for a in report.actions] == ["create", "create"]

    def test_creates_project_and_services(self, mocker):
        """We expect create+update calls for a new project with services."""
        manifest = Manifest.model_validate(
            {
                "connection": "test-env",
                "projects": [
                    {
                        "name": "app",
                        "services": [
                            {"type": "compose", "name": "backend", "compose_file": "version: '3'"},
                            {"type": "application", "name": "web", "image": "nginx:latest"},
                        ],
                    }
                ],
            }
        )
        client = _applier(mocker, State(connection="test-env"))

        report = Applier(manifest, _connection()).run()

        paths = [call.args[1] for call in client.request.call_args_list]
        assert "project.create" in paths
        assert "compose.create" in paths
        assert "compose.update" in paths
        assert "application.create" in paths
        assert "application.update" in paths
        assert [a.action for a in report.actions] == ["create", "create", "create"]


class TestApplyUpdate:
    """Update flows."""

    def test_updates_changed_fields(self, mocker):
        """We expect an update with only the changed fields."""
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
        state = State(
            connection="test-env",
            projects=[_project_live("app", [_compose_live("backend", "s1")])],
        )
        client = _applier(mocker, state)

        report = Applier(manifest, _connection()).run()

        update_calls = [call for call in client.request.call_args_list if call.args[1] == "compose.update"]
        assert len(update_calls) == 1
        body = update_calls[0].args[2]["body"]
        assert body["composeId"] == "s1"
        assert "composeFile" in body
        assert [a.action for a in report.actions] == ["update"]

    def test_resolves_env_secret_refs_before_update(self, mocker):
        """We expect env {cmd} refs to be resolved before compare/send."""
        manifest = Manifest.model_validate(
            {
                "connection": "test-env",
                "projects": [
                    {
                        "name": "app",
                        "services": [
                            {
                                "type": "compose",
                                "name": "backend",
                                "compose_file": "version: '3'",
                                "env": 'PASSWORD={cmd: "echo hunter2"}\nPLAIN=value',
                            }
                        ],
                    }
                ],
            }
        )
        state = State(
            connection="test-env",
            projects=[_project_live("app", [_compose_live("backend", "s1", env="PASSWORD=old\nPLAIN=value")])],
        )
        client = _applier(mocker, state)

        report = Applier(manifest, _connection()).run()

        update_calls = [call for call in client.request.call_args_list if call.args[1] == "compose.update"]
        assert len(update_calls) == 1
        body = update_calls[0].args[2]["body"]
        assert body["env"] == "PASSWORD=hunter2\nPLAIN=value"
        assert [a.action for a in report.actions] == ["update"]

    def test_env_secret_ref_matching_skips_update(self, mocker):
        """We expect no update when the resolved env equals the live env."""
        manifest = Manifest.model_validate(
            {
                "connection": "test-env",
                "projects": [
                    {
                        "name": "app",
                        "services": [
                            {
                                "type": "compose",
                                "name": "backend",
                                "compose_file": "version: '3'",
                                "env": 'PASSWORD={cmd: "echo hunter2"}\nPLAIN=value',
                            }
                        ],
                    }
                ],
            }
        )
        state = State(
            connection="test-env",
            projects=[_project_live("app", [_compose_live("backend", "s1", env="PASSWORD=hunter2\nPLAIN=value")])],
        )
        client = _applier(mocker, state)

        report = Applier(manifest, _connection()).run()

        assert not any(call.args[1] == "compose.update" for call in client.request.call_args_list)
        assert [a.action for a in report.actions] == []

    def test_no_changes_skips_update(self, mocker):
        """We expect no update when the service already matches."""
        manifest = Manifest.model_validate(
            {
                "connection": "test-env",
                "projects": [
                    {
                        "name": "app",
                        "services": [{"type": "compose", "name": "backend", "compose_file": "version: '3'"}],
                    }
                ],
            }
        )
        state = State(
            connection="test-env",
            projects=[_project_live("app", [_compose_live("backend", "s1")])],
        )
        client = _applier(mocker, state)

        report = Applier(manifest, _connection()).run()

        assert [a.action for a in report.actions] == []
        assert not any(call.args[1].endswith(".update") for call in client.request.call_args_list)


class TestApplyGitProviders:
    """Git provider handling."""

    def test_missing_provider_skips_service(self, mocker):
        """We expect services depending on a missing provider to be skipped."""
        manifest = Manifest.model_validate(
            {
                "connection": "test-env",
                "git_providers": [{"name": "github-main", "provider": "github"}],
                "projects": [
                    {
                        "name": "app",
                        "services": [
                            {
                                "type": "compose",
                                "name": "backend",
                                "source": {"provider": "github-main", "repository": "acme/backend", "branch": "main"},
                            }
                        ],
                    }
                ],
            }
        )
        _applier(mocker, State(connection="test-env"))

        report = Applier(manifest, _connection()).run()

        assert any(a.action == "validate" for a in report.actions)
        assert any(a.action == "skip" and "not configured" in a.details for a in report.actions)

    def test_uses_provider_subtype_id(self, mocker):
        """We expect the provider subtype id to be set on the service."""
        manifest = Manifest.model_validate(
            {
                "connection": "test-env",
                "git_providers": [{"name": "github-main", "provider": "github"}],
                "projects": [
                    {
                        "name": "app",
                        "services": [
                            {
                                "type": "compose",
                                "name": "backend",
                                "source": {"provider": "github-main", "repository": "acme/backend", "branch": "main"},
                            }
                        ],
                    }
                ],
            }
        )
        state = State(
            connection="test-env",
            git_providers=[_provider_live("github-main", "github", github_id="gh-123")],
        )
        client = _applier(mocker, state)

        Applier(manifest, _connection()).run()

        update_calls = [call for call in client.request.call_args_list if call.args[1] == "compose.update"]
        assert update_calls
        body = update_calls[0].args[2]["body"]
        assert body["sourceType"] == "github"
        assert body["githubId"] == "gh-123"
        assert body["repository"] == "backend"
        assert body["owner"] == "acme"


class TestApplyDeploy:
    """Deploy flag."""

    def test_deploy_after_create(self, mocker):
        """We expect a deploy call after creating a service."""
        manifest = Manifest.model_validate(
            {
                "connection": "test-env",
                "projects": [
                    {"name": "app", "services": [{"type": "compose", "name": "backend", "compose_file": "x: 1"}]}
                ],
            }
        )
        client = _applier(mocker, State(connection="test-env"))

        Applier(manifest, _connection(), deploy=True).run()

        deploy_calls = [call for call in client.request.call_args_list if call.args[1] == "compose.deploy"]
        assert len(deploy_calls) == 1
        assert deploy_calls[0].args[2]["body"] == {"composeId": "c-new"}


class TestApplyEnvironments:
    """Multi-environment apply flows."""

    def test_creates_missing_environment(self, mocker):
        """We expect a named environment to be created when missing."""
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
        state = State(connection="test-env", projects=[_project_live("app", [])])
        client = _applier(mocker, state)

        Applier(manifest, _connection()).run()

        env_calls = [call for call in client.request.call_args_list if call.args[1] == "environment.create"]
        assert len(env_calls) == 1
        assert env_calls[0].args[2]["body"] == {"projectId": "app", "name": "staging"}
        compose_calls = [call for call in client.request.call_args_list if call.args[1] == "compose.create"]
        assert compose_calls
        assert compose_calls[0].args[2]["body"]["environmentId"] == "env-staging"

    def test_uses_existing_environment(self, mocker):
        """We expect existing named environments to be reused."""
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
        staging = LiveEnvironment(
            environment_id="e-staging",
            name="staging",
            is_default=False,
            services=[],
        )
        state = State(
            connection="test-env",
            projects=[
                LiveProject(
                    project_id="app",
                    name="app",
                    environments=[
                        LiveEnvironment(
                            environment_id="e1",
                            name="production",
                            is_default=True,
                            services=[],
                        ),
                        staging,
                    ],
                )
            ],
        )
        client = _applier(mocker, state)

        Applier(manifest, _connection()).run()

        env_calls = [call for call in client.request.call_args_list if call.args[1] == "environment.create"]
        assert env_calls == []
        compose_calls = [call for call in client.request.call_args_list if call.args[1] == "compose.create"]
        assert compose_calls
        assert compose_calls[0].args[2]["body"]["environmentId"] == "e-staging"


class TestApplyDatabases:
    """Database apply flows."""

    def test_creates_database_with_password_cmd(self, mocker):
        """We expect a postgres create with a resolved password."""
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
                                "password_cmd": "echo secret123",
                            }
                        ],
                    }
                ],
            }
        )
        client = _applier(mocker, State(connection="test-env"))

        Applier(manifest, _connection()).run()

        create_calls = [call for call in client.request.call_args_list if call.args[1] == "postgres.create"]
        assert len(create_calls) == 1
        body = create_calls[0].args[2]["body"]
        assert body["databasePassword"] == "secret123"
        assert body["databaseName"] == "db"
        assert body["databaseUser"] == "db"
        assert body["environmentId"] == "e-new"

    def test_password_cmd_runs_through_shell(self, mocker):
        """We expect password_cmd to support shell pipelines."""
        manifest = Manifest.model_validate(
            {
                "connection": "test-env",
                "projects": [
                    {
                        "name": "app",
                        "services": [
                            {
                                "type": "redis",
                                "name": "cache",
                                "password_cmd": "printf hunter2 | tr a-z A-Z",
                            }
                        ],
                    }
                ],
            }
        )
        client = _applier(mocker, State(connection="test-env"))
        check_output = mocker.patch("dokli.apply.subprocess.check_output", return_value=b"HUNTER2")

        Applier(manifest, _connection()).run()

        check_output.assert_called_with("printf hunter2 | tr a-z A-Z", shell=True)
        create_calls = [call for call in client.request.call_args_list if call.args[1] == "redis.create"]
        assert create_calls[0].args[2]["body"]["databasePassword"] == "HUNTER2"

    def test_generates_password_when_missing(self, mocker):
        """We expect a generated password with a warning when none is provided."""
        manifest = Manifest.model_validate(
            {
                "connection": "test-env",
                "projects": [{"name": "app", "services": [{"type": "redis", "name": "cache"}]}],
            }
        )
        _applier(mocker, State(connection="test-env"))

        report = Applier(manifest, _connection()).run()

        assert any("generated a random password" in warning for warning in report.warnings)
        assert report.actions

    def test_updates_database(self, mocker):
        """We expect a database update when fields differ."""
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
                                "password_cmd": "echo secret123",
                            }
                        ],
                    }
                ],
            }
        )
        live = LiveService(
            service_id="pg1",
            app_name="db",
            type="postgres",
            name="db",
            database_name="olddb",
            database_user="db",
            database_password="secret123",
        )
        state = State(
            connection="test-env",
            projects=[
                LiveProject(
                    project_id="app",
                    name="app",
                    environments=[
                        LiveEnvironment(
                            environment_id="e1",
                            name="production",
                            is_default=True,
                            services=[live],
                        )
                    ],
                )
            ],
        )
        client = _applier(mocker, state)

        Applier(manifest, _connection()).run()

        update_calls = [call for call in client.request.call_args_list if call.args[1] == "postgres.update"]
        assert len(update_calls) == 1
        body = update_calls[0].args[2]["body"]
        assert body["postgresId"] == "pg1"
        assert body["databaseName"] == "newdb"
        assert "databasePassword" not in body  # password unchanged
