"""State collection tests."""

from dokli.config import ConnectionConfig
from dokli.state import State, collect_state


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


def _responses():
    return {
        "project.all": [{"projectId": "p1", "name": "myapp", "description": None}],
        "project.one": {
            "projectId": "p1",
            "name": "myapp",
            "description": None,
            "environments": [
                {
                    "environmentId": "e1",
                    "name": "production",
                    "isDefault": True,
                    "compose": [
                        {
                            "composeId": "c1",
                            "appName": "backend",
                            "name": "backend",
                            "sourceType": "github",
                            "githubId": "gh1",
                            "repository": "jonykalavera/backend",
                            "owner": "jonykalavera",
                            "branch": "main",
                            "composePath": "docker-compose.yml",
                            "serverId": "srv1",
                            "description": None,
                        }
                    ],
                    "applications": [
                        {
                            "applicationId": "a1",
                            "appName": "web",
                            "name": "web",
                            "sourceType": "github",
                            "githubId": "gh1",
                            "repository": "jonykalavera/web",
                            "owner": "jonykalavera",
                            "branch": "main",
                            "buildType": "dockerfile",
                            "dockerfileLocation": "./web/Dockerfile",
                            "serverId": "srv1",
                            "description": None,
                        }
                    ],
                }
            ],
        },
        "gitProvider.getAll": [
            {
                "gitProviderId": "gp1",
                "name": "github-main",
                "providerType": "github",
                "isConfigured": True,
                "github": {"githubId": "gh1", "githubAppName": "dokli", "isConfigured": True},
                "gitlab": None,
                "gitea": None,
                "bitbucket": None,
            }
        ],
        "server.all": [{"serverId": "srv1", "name": "local"}],
    }


class TestCollectState:
    """State collection tests."""

    def test_collect_state(self, mocker):
        """We expect a normalized state with projects, services and providers."""
        responses = _responses()
        client = mocker.Mock()
        client.request.side_effect = lambda _method, path, _params: FakeResponse(responses[path])
        mocker.patch("dokli.state.APIClient", return_value=client)

        state = collect_state(_connection())

        assert isinstance(state, State)
        assert state.connection == "test-env"
        assert len(state.servers) == 1
        assert state.servers[0].name == "local"

        project = state.projects[0]
        assert project.project_id == "p1"
        assert len(project.environments) == 1
        environment = project.environments[0]
        assert environment.is_default
        assert [s.name for s in environment.services] == ["backend", "web"]

        compose = environment.services[0]
        assert compose.type == "compose"
        assert compose.provider == "github-main"
        assert compose.repository == "jonykalavera/backend"
        assert compose.compose_path == "docker-compose.yml"

        application = environment.services[1]
        assert application.type == "application"
        assert application.build_type == "dockerfile"
        assert application.dockerfile_location == "./web/Dockerfile"

        provider = state.git_providers[0]
        assert provider.name == "github-main"
        assert provider.github_id == "gh1"
        assert provider.is_configured

    def test_request_paths(self, mocker):
        """We expect state to read projects, git providers and servers."""
        responses = _responses()
        client = mocker.Mock()
        client.request.side_effect = lambda _method, path, _params: FakeResponse(responses[path])
        mocker.patch("dokli.state.APIClient", return_value=client)

        collect_state(_connection())

        paths = [call.args[1] for call in client.request.call_args_list]
        assert "project.all" in paths
        assert "project.one" in paths
        assert "gitProvider.getAll" in paths
        assert "server.all" in paths

    def test_collects_database_services(self, mocker):
        """We expect database services to be collected."""
        responses = _responses()
        responses["project.one"]["environments"][0]["postgres"] = [
            {
                "postgresId": "pg1",
                "appName": "db",
                "name": "db",
                "databaseName": "appdb",
                "databaseUser": "app",
                "databasePassword": "hunter2",
                "dockerImage": "postgres:16",
                "serverId": "srv1",
                "description": None,
            }
        ]
        client = mocker.Mock()
        client.request.side_effect = lambda _method, path, _params: FakeResponse(responses[path])
        mocker.patch("dokli.state.APIClient", return_value=client)

        state = collect_state(_connection())

        service = state.projects[0].environments[0].services[-1]
        assert service.type == "postgres"
        assert service.service_id == "pg1"
        assert service.database_name == "appdb"
        assert service.database_user == "app"
        assert service.database_password == "hunter2"

    def test_enriches_summary_compose_via_one(self, mocker):
        """We expect summary compose records to be enriched via compose.one."""
        responses = _responses()
        responses["project.one"]["environments"][0]["compose"] = [
            {"composeId": "c1", "appName": "backend", "name": "backend", "serverId": "srv1", "description": None}
        ]
        responses["compose.one"] = {
            "composeId": "c1",
            "appName": "backend",
            "name": "backend",
            "sourceType": "raw",
            "composeFile": "services:\n  web:\n    image: nginx:latest\n",
            "command": "",
            "env": "FOO=bar",
            "serverId": "srv1",
        }
        client = mocker.Mock()
        client.request.side_effect = lambda _method, path, _params: FakeResponse(responses[path])
        mocker.patch("dokli.state.APIClient", return_value=client)

        state = collect_state(_connection())

        compose = state.projects[0].environments[0].services[0]
        assert compose.type == "compose"
        assert compose.compose_file == "services:\n  web:\n    image: nginx:latest\n"
        assert compose.source_type == "raw"
        assert compose.env == "FOO=bar"
        one_call = next(
            call for call in client.request.call_args_list if call.args[1] == "compose.one"
        )
        assert one_call.args[2] == {"composeId": "c1"}

    def test_full_record_skips_one_fetch(self, mocker):
        """We expect no <type>.one call when the record already has detail."""
        responses = _responses()
        client = mocker.Mock()
        client.request.side_effect = lambda _method, path, _params: FakeResponse(responses[path])
        mocker.patch("dokli.state.APIClient", return_value=client)

        collect_state(_connection())

        assert not any(call.args[1].endswith(".one") and not call.args[1].startswith("project")
                       for call in client.request.call_args_list)

    def test_summary_falls_back_when_one_fails(self, mocker):
        """We expect a failed <type>.one to keep the summary record."""

        def _request(_method, path, _params):
            if path == "compose.one":
                raise RuntimeError("boom")
            return FakeResponse(_responses()[path])

        responses = _responses()
        responses["project.one"]["environments"][0]["compose"] = [
            {"composeId": "c1", "appName": "backend", "name": "backend", "serverId": "srv1", "description": None}
        ]
        client = mocker.Mock()
        client.request.side_effect = _request
        mocker.patch("dokli.state.APIClient", return_value=client)

        state = collect_state(_connection())

        compose = state.projects[0].environments[0].services[0]
        assert compose.type == "compose"
        assert compose.name == "backend"
        assert compose.compose_file is None
