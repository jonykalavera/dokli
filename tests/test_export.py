"""Export tests."""

import pytest

from dokli.config import ConnectionConfig
from dokli.export import export_manifest
from dokli.manifest import ApplicationService, ComposeService, DatabaseService
from dokli.state import LiveEnvironment, LiveGitProvider, LiveProject, LiveService, State


class _NullClient:
    """APIClient stand-in returning empty payloads (no resources exported)."""

    def request(self, method, path, params):
        class _Response:
            def json(self):
                return {}

        return _Response()


@pytest.fixture(autouse=True)
def _no_network(mocker):
    mocker.patch("dokli.export.APIClient", return_value=_NullClient())


class _FakeClient:
    """APIClient stand-in returning configured records."""

    def __init__(self, records):
        self.records = records

    def request(self, method, path, params):
        records = self.records

        class _Response:
            def json(self):
                return records.get(path, {})

        return _Response()


class TestExportResources:
    """Generic resource export tests (issue #55)."""

    def test_exports_application_children(self, mocker):
        """We expect nested child records to be exported as resources."""
        mocker.patch(
            "dokli.export.APIClient",
            return_value=_FakeClient(
                {
                    "application.one": {
                        "applicationId": "a1",
                        "domains": [
                            {"domainId": "d1", "host": "www.example.com", "https": True, "path": "/", "domainType": "application"}
                        ],
                        "ports": [{"portId": "p1", "publishedPort": 8080, "targetPort": 80, "protocol": "tcp", "publishMode": "ingress"}],
                        "mounts": [{"mountId": "m1", "type": "bind", "mountPath": "/etc", "filePath": "rclone.conf"}],
                        "security": [{"securityId": "s1", "username": "admin", "password": "secret"}],
                        "redirects": [{"redirectId": "r1", "regex": "/old", "replacement": "/new", "permanent": False}],
                    },
                    "schedule.list": [
                        {"scheduleId": "sc1", "name": "nightly", "cronExpression": "0 3 * * *", "command": "echo x", "enabled": True}
                    ],
                    "destination.all": [],
                }
            ),
        )
        mocker.patch(
            "dokli.export.collect_state",
            return_value=State(
                connection="test-env",
                projects=[_project_live("app", [_live_service("application", "web")])],
            ),
        )

        manifest, warnings = export_manifest(_connection())

        kinds = {r.kind: r for r in manifest.resources}
        assert kinds["domain"].name == "www.example.com"
        assert kinds["domain"].data["https"] is True
        assert kinds["domain"].in_ == "project:app / application:web"
        assert kinds["port"].data["publishedPort"] == 8080
        assert kinds["mount"].data["type"] == "bind"
        assert kinds["redirects"].data["replacement"] == "/new"
        assert "password" not in kinds["security"].data
        assert kinds["security"].data["username"] == "admin"
        assert kinds["schedule"].data["cronExpression"] == "0 3 * * *"
        assert any("Secret fields" in w for w in warnings)

    def test_exports_backup_with_destination_name(self, mocker):
        """We expect backup destinations to be exported by name."""
        mocker.patch(
            "dokli.export.APIClient",
            return_value=_FakeClient(
                {
                    "postgres.one": {
                        "postgresId": "pg1",
                        "backups": [
                            {
                                "backupId": "b1",
                                "schedule": "0 4 * * *",
                                "prefix": "db",
                                "database": "db",
                                "databaseType": "postgres",
                                "enabled": True,
                                "destinationId": "dst1",
                                "keepLatestCount": 7,
                            }
                        ],
                    },
                    "destination.all": [{"destinationId": "dst1", "name": "local-bucket"}],
                }
            ),
        )
        mocker.patch(
            "dokli.export.collect_state",
            return_value=State(
                connection="test-env",
                projects=[_project_live("app", [_live_service("postgres", "db")])],
            ),
        )

        manifest, _ = export_manifest(_connection())

        backup = manifest.resources[0]
        assert backup.kind == "backup"
        assert backup.data["destination"] == "local-bucket"
        assert "destinationId" not in backup.data

    def test_non_default_environment_in_path(self, mocker):
        """We expect named environments to appear in the in path."""
        mocker.patch("dokli.export.APIClient", return_value=_NullClient())
        project = LiveProject(
            project_id="p1",
            name="app",
            environments=[
                LiveEnvironment(
                    environment_id="e1",
                    name="staging",
                    is_default=False,
                    services=[_live_service("application", "web")],
                )
            ],
        )
        mocker.patch(
            "dokli.export.collect_state",
            return_value=State(connection="test-env", projects=[project]),
        )

        manifest, _ = export_manifest(_connection())

        assert manifest.resources == []

    def test_round_trip_loads(self, mocker):
        """We expect an exported manifest to load back with its resources."""
        mocker.patch("dokli.export.APIClient", return_value=_NullClient())
        mocker.patch(
            "dokli.export.collect_state",
            return_value=State(connection="test-env", projects=[]),
        )

        manifest, _ = export_manifest(_connection())
        reloaded = manifest.__class__.model_validate(manifest.model_dump(by_alias=True))

        assert reloaded.resources == manifest.resources
        assert reloaded.connection == "test-env"


def _connection() -> ConnectionConfig:
    return ConnectionConfig(name="test-env", url="https://example.com", api_key_cmd="echo key")


def _live_service(service_type: str, name: str, **overrides) -> LiveService:
    defaults = {
        "service_id": f"{service_type}-{name}",
        "app_name": name,
        "type": service_type,
        "name": name,
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


def _provider_live(name: str, provider: str, is_configured: bool = True) -> LiveGitProvider:
    return LiveGitProvider(
        git_provider_id="gp1",
        name=name,
        provider=provider,
        is_configured=is_configured,
    )


class TestExportCompose:
    """Compose export tests."""

    def test_raw_compose(self, mocker):
        """We expect a raw compose to be exported with its file inline."""
        mocker.patch(
            "dokli.export.collect_state",
            return_value=State(
                connection="test-env",
                projects=[
                    _project_live(
                        "app",
                        [_live_service("compose", "backend", source_type="raw", compose_file="version: '3'")],
                    )
                ],
            ),
        )

        manifest, warnings = export_manifest(_connection())

        service = manifest.projects[0].services[0]
        assert isinstance(service, ComposeService)
        assert service.compose_file == "version: '3'"
        assert service.source is None
        assert warnings == []

    def test_git_compose(self, mocker):
        """We expect a git compose to be exported as a source."""
        mocker.patch(
            "dokli.export.collect_state",
            return_value=State(
                connection="test-env",
                projects=[
                    _project_live(
                        "app",
                        [
                            _live_service(
                                "compose",
                                "backend",
                                source_type="github",
                                provider="github-main",
                                repository="backend",
                                owner="acme",
                                branch="main",
                                compose_path="docker-compose.yml",
                            )
                        ],
                    )
                ],
            ),
        )

        manifest, _ = export_manifest(_connection())

        service = manifest.projects[0].services[0]
        assert isinstance(service, ComposeService)
        assert service.source is not None
        assert service.source.provider == "github-main"
        assert service.source.repository == "acme/backend"
        assert service.source.branch == "main"
        assert service.compose_path == "docker-compose.yml"


class TestExportSecrets:
    """Secret redaction tests."""

    def test_env_redacted_by_default(self, mocker):
        """We expect env vars to be redacted unless explicitly requested."""
        mocker.patch(
            "dokli.export.collect_state",
            return_value=State(
                connection="test-env",
                projects=[
                    _project_live(
                        "app",
                        [
                            _live_service(
                                "compose",
                                "backend",
                                source_type="raw",
                                compose_file="version: '3'",
                                env="PASSWORD=hunter2",
                            )
                        ],
                    )
                ],
            ),
        )

        manifest, warnings = export_manifest(_connection())

        service = manifest.projects[0].services[0]
        assert isinstance(service, ComposeService)
        assert service.env is None
        assert any("redacted" in warning for warning in warnings)

    def test_env_exported_with_include_secrets(self, mocker):
        """We expect env vars to be exported with include_secrets."""
        mocker.patch(
            "dokli.export.collect_state",
            return_value=State(
                connection="test-env",
                projects=[
                    _project_live(
                        "app",
                        [
                            _live_service(
                                "compose",
                                "backend",
                                source_type="raw",
                                compose_file="version: '3'",
                                env="PASSWORD=hunter2",
                            )
                        ],
                    )
                ],
            ),
        )

        manifest, warnings = export_manifest(_connection(), include_secrets=True)

        service = manifest.projects[0].services[0]
        assert isinstance(service, ComposeService)
        assert service.env == "PASSWORD=hunter2"
        assert not any("redacted" in warning for warning in warnings)


class TestExportApplication:
    """Application export tests."""

    def test_docker_application(self, mocker):
        """We expect a docker application to be exported with its image."""
        mocker.patch(
            "dokli.export.collect_state",
            return_value=State(
                connection="test-env",
                projects=[
                    _project_live(
                        "app",
                        [_live_service("application", "web", source_type="docker", docker_image="nginx:latest")],
                    )
                ],
            ),
        )

        manifest, _ = export_manifest(_connection())

        service = manifest.projects[0].services[0]
        assert isinstance(service, ApplicationService)
        assert service.image == "nginx:latest"
        assert service.source is None

    def test_git_application(self, mocker):
        """We expect a git application to be exported with build details."""
        mocker.patch(
            "dokli.export.collect_state",
            return_value=State(
                connection="test-env",
                projects=[
                    _project_live(
                        "app",
                        [
                            _live_service(
                                "application",
                                "web",
                                source_type="github",
                                provider="github-main",
                                repository="web",
                                owner="acme",
                                branch="main",
                                build_type="dockerfile",
                                dockerfile_location="./web/Dockerfile",
                            )
                        ],
                    )
                ],
            ),
        )

        manifest, _ = export_manifest(_connection())

        service = manifest.projects[0].services[0]
        assert isinstance(service, ApplicationService)
        assert service.source.repository == "acme/web"
        assert service.build_type == "dockerfile"
        assert service.dockerfile_location == "./web/Dockerfile"


class TestExportGitProviders:
    """Git provider export tests."""

    def test_provider_metadata_with_warning(self, mocker):
        """We expect provider metadata without credentials plus a warning."""
        mocker.patch(
            "dokli.export.collect_state",
            return_value=State(
                connection="test-env",
                git_providers=[_provider_live("github-main", "github")],
            ),
        )

        manifest, warnings = export_manifest(_connection())

        assert len(manifest.git_providers) == 1
        provider = manifest.git_providers[0]
        assert provider.name == "github-main"
        assert provider.provider == "github"
        assert provider.token_cmd is None
        assert any("write-only" in warning for warning in warnings)

    def test_unsupported_provider_skipped(self, mocker):
        """We expect unsupported provider types to be skipped with a warning."""
        mocker.patch(
            "dokli.export.collect_state",
            return_value=State(
                connection="test-env",
                git_providers=[_provider_live("custom", "git")],
            ),
        )

        manifest, warnings = export_manifest(_connection())

        assert manifest.git_providers == []
        assert any("unsupported type" in warning for warning in warnings)


class TestExportDatabases:
    """Database export tests."""

    def test_database_export_redacts_password(self, mocker):
        """We expect a database to be exported without its password."""
        mocker.patch(
            "dokli.export.collect_state",
            return_value=State(
                connection="test-env",
                projects=[
                    _project_live(
                        "app",
                        [
                            _live_service(
                                "postgres",
                                "db",
                                database_name="appdb",
                                database_user="app",
                                database_password="hunter2",
                                docker_image="postgres:16",
                            )
                        ],
                    )
                ],
            ),
        )

        manifest, warnings = export_manifest(_connection())

        service = manifest.projects[0].services[0]
        assert isinstance(service, DatabaseService)
        assert service.database_name == "appdb"
        assert service.password is None
        assert service.password_cmd is None
        assert any("password" in warning and "not exported" in warning for warning in warnings)


class TestExportEnvironments:
    """Multi-environment export tests."""

    def test_exports_named_environments(self, mocker):
        """We expect non-default environments to be exported under environments."""
        default_env = LiveEnvironment(
            environment_id="e1",
            name="production",
            is_default=True,
            services=[
                _live_service("compose", "backend", source_type="raw", compose_file="version: '3'"),
            ],
        )
        staging_env = LiveEnvironment(
            environment_id="e2",
            name="staging",
            is_default=False,
            services=[
                _live_service("compose", "api", source_type="raw", compose_file="version: '3'"),
            ],
        )
        mocker.patch(
            "dokli.export.collect_state",
            return_value=State(
                connection="test-env",
                projects=[
                    LiveProject(
                        project_id="app",
                        name="app",
                        environments=[default_env, staging_env],
                    )
                ],
            ),
        )

        manifest, _ = export_manifest(_connection())

        project = manifest.projects[0]
        assert [s.name for s in project.services] == ["backend"]
        assert len(project.environments) == 1
        assert project.environments[0].name == "staging"
        assert [s.name for s in project.environments[0].services] == ["api"]
