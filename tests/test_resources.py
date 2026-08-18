"""Generic resources tests (issue #50)."""

import pytest

from dokli.manifest import Manifest, Resource
from dokli.report import ApplyReport
from dokli.resources import (
    CHILD_ARRAY,
    MATCH_KEYS,
    SERVICE_KINDS,
    ResourceManager,
    child_array_key,
    match_key,
    parse_in,
    resolve_data,
)


class TestMaps:
    """Curated resource maps."""

    def test_match_keys(self):
        """We expect the curated match keys for kinds without a stable name."""
        assert MATCH_KEYS["domain"] == "host"
        assert MATCH_KEYS["port"] == "publishedPort"
        assert MATCH_KEYS["mount"] == "filePath"
        assert match_key("compose") == "name"

    def test_child_array_keys(self):
        """We expect child kinds to map to their nested array key."""
        assert child_array_key("domain") == "domains"
        assert child_array_key("port") == "ports"
        assert child_array_key("mount") == "mounts"
        assert CHILD_ARRAY["backup"] == "backups"

    def test_parse_in(self):
        """We expect in paths to parse into (kind, name) segments."""
        assert parse_in("compose:torrents") == [("compose", "torrents")]
        assert parse_in("project:media / environment:production / compose:web") == [
            ("project", "media"),
            ("environment", "production"),
            ("compose", "web"),
        ]
        assert parse_in(None) == []

    def test_resolve_data(self, fake_keyring):
        """We expect dict secret refs to resolve at apply time."""
        fake_keyring.store[("dokli", "db.main")] = "secret"
        assert resolve_data({"databasePassword": {"keyring": "db.main"}}) == {"databasePassword": "secret"}


def _service(kind, name, service_id):
    return type("S", (), {"type": kind, "name": name, "service_id": service_id})()


def _state(services):
    project = type(
        "P",
        (),
        {
            "name": "media",
            "environments": [
                type("E", (), {"name": "production", "environment_id": "e1", "services": services})()
            ],
        },
    )()
    return type("S", (), {"projects": [project]})()


class FakeClient:
    """Minimal APIClient stand-in returning configurable records."""

    def __init__(self, records=None):
        self.calls = []
        self.records = records or {}

    def request(self, method, path, params):
        self.calls.append((method, path, params))
        record = self.records.get(path, {})

        class _Response:
            def json(self):
                return record

        return _Response()


def _manager(manifest, client, services):
    applier = type("A", (), {})()
    applier.manifest = manifest
    applier.client = client
    applier.report = ApplyReport()
    applier._state = _state(services)
    return ResourceManager(applier)


def _manifest(*resources):
    return Manifest(connection="test", resources=list(resources))


class TestResourceManager:
    """Generic leaf resource application."""

    def test_create_domain(self):
        """We expect a missing domain to be created with its parent id."""
        client = FakeClient({"compose.one": {"composeId": "c1", "domains": []}})
        manager = _manager(
            _manifest(Resource(kind="domain", name="x.example.com", in_="compose:web", data={"host": "x.example.com"})),
            client,
            [_service("compose", "web", "c1")],
        )
        manager.run()
        create = next(c for c in client.calls if c[1] == "domain.create")
        assert create[2] == {"body": {"host": "x.example.com", "composeId": "c1"}}
        assert manager.report.actions[0].action == "create"
        assert manager.report.actions[0].kind == "domain"

    def test_update_domain(self):
        """We expect a changed domain to be updated."""
        client = FakeClient(
            {
                "compose.one": {
                    "composeId": "c1",
                    "domains": [{"domainId": "d1", "host": "x.example.com", "port": 80}],
                }
            }
        )
        manager = _manager(
            _manifest(
                Resource(
                    kind="domain",
                    name="x.example.com",
                    in_="compose:web",
                    data={"host": "x.example.com", "port": 443},
                )
            ),
            client,
            [_service("compose", "web", "c1")],
        )
        manager.run()
        update = next(c for c in client.calls if c[1] == "domain.update")
        assert update[2] == {"body": {"host": "x.example.com", "port": 443, "composeId": "c1", "domainId": "d1"}}
        assert manager.report.actions[0].action == "update"

    def test_skip_unchanged_domain(self):
        """We expect an unchanged domain to be skipped."""
        client = FakeClient(
            {"compose.one": {"composeId": "c1", "domains": [{"domainId": "d1", "host": "x.example.com", "port": 80}]}}
        )
        manager = _manager(
            _manifest(
                Resource(kind="domain", name="x.example.com", in_="compose:web", data={"host": "x.example.com", "port": 80})
            ),
            client,
            [_service("compose", "web", "c1")],
        )
        manager.run()
        assert manager.report.actions[0].action == "skip"
        assert not any(c[1] in ("domain.create", "domain.update") for c in client.calls)

    def test_ambiguous_parent(self):
        """We expect an error when the parent service name is ambiguous."""
        client = FakeClient({})
        manager = _manager(
            _manifest(Resource(kind="domain", name="x.example.com", in_="compose:web", data={"host": "x.example.com"})),
            client,
            [_service("compose", "web", "c1"), _service("compose", "web", "c2")],
        )
        with pytest.raises(ValueError):
            manager.run()

    def test_mount_uses_service_id(self):
        """We expect mounts to address their parent via serviceId + serviceType
        and to route to the mounts entity."""
        client = FakeClient({"compose.one": {"composeId": "c1", "mounts": []}})
        manager = _manager(
            _manifest(
                Resource(kind="mount", name="rclone.conf", in_="compose:web", data={"filePath": "rclone.conf", "mountPath": "/"})
            ),
            client,
            [_service("compose", "web", "c1")],
        )
        manager.run()
        create = next(c for c in client.calls if c[1] == "mounts.create")
        body = create[2]["body"]
        assert body["serviceId"] == "c1"
        assert body["serviceType"] == "compose"

    def test_port_parent_uses_application_id(self):
        """We expect ports to address their parent with applicationId."""
        client = FakeClient({"application.one": {"applicationId": "a1", "ports": []}})
        manager = _manager(
            _manifest(
                Resource(
                    kind="port",
                    name="8080",
                    in_="application:api",
                    data={"publishedPort": 8080, "targetPort": 80, "protocol": "tcp"},
                )
            ),
            client,
            [_service("application", "api", "a1")],
        )
        manager.run()
        create = next(c for c in client.calls if c[1] == "port.create")
        assert create[2]["body"]["applicationId"] == "a1"

    def test_port_wrong_parent_rejected(self):
        """We expect ports under a non-application parent to fail."""
        client = FakeClient({})
        manager = _manager(
            _manifest(Resource(kind="port", name="8080", in_="compose:web", data={"publishedPort": 8080})),
            client,
            [_service("compose", "web", "c1")],
        )
        with pytest.raises(ValueError):
            manager.run()

    def test_ancestor_path_disambiguates(self):
        """We expect ancestor segments to scope the parent lookup."""
        client = FakeClient({"compose.one": {"composeId": "c1", "domains": []}})
        manager = _manager(
            _manifest(
                Resource(
                    kind="domain",
                    name="x.example.com",
                    in_="project:media / environment:production / compose:web",
                    data={"host": "x.example.com"},
                )
            ),
            client,
            [_service("compose", "web", "c1")],
        )
        manager.run()
        assert manager.report.actions[0].action == "create"

    def test_missing_field_triggers_update(self):
        """We expect a desired field absent from the live record to be set."""
        client = FakeClient(
            {"compose.one": {"composeId": "c1", "domains": [{"domainId": "d1", "host": "x.example.com"}]}}
        )
        manager = _manager(
            _manifest(
                Resource(
                    kind="domain",
                    name="x.example.com",
                    in_="compose:web",
                    data={"host": "x.example.com", "https": True},
                )
            ),
            client,
            [_service("compose", "web", "c1")],
        )
        manager.run()
        assert manager.report.actions[0].action == "update"

    def test_missing_parent_records_skip(self):
        """We expect a missing parent to record a skip action, not abort."""
        client = FakeClient({})
        manager = _manager(
            _manifest(Resource(kind="domain", name="x.example.com", in_="compose:nope", data={"host": "x.example.com"})),
            client,
            [],
        )
        manager.run()
        assert manager.report.actions[0].action == "skip"
        assert "not found" in manager.report.actions[0].details

    def test_schedule_lists_via_list_route(self):
        """We expect schedules to be fetched via schedule.list, not a nested array."""
        client = FakeClient(
            {
                "application.one": {"applicationId": "a1"},
                "schedule.list": [
                    {"scheduleId": "s1", "name": "nightly", "cronExpression": "0 3 * * *", "command": "echo x"}
                ],
            }
        )
        manager = _manager(
            _manifest(
                Resource(
                    kind="schedule",
                    name="nightly",
                    in_="application:api",
                    data={"name": "nightly", "cronExpression": "0 3 * * *", "command": "echo x"},
                )
            ),
            client,
            [_service("application", "api", "a1")],
        )
        manager.run()
        assert manager.report.actions[0].action == "skip"
        call = next(c for c in client.calls if c[1] == "schedule.list")
        assert call[2] == {"id": "a1", "scheduleType": "application"}

    def test_schedule_created_when_missing(self):
        """We expect a missing schedule to be created with its parent id."""
        client = FakeClient({"application.one": {"applicationId": "a1"}, "schedule.list": []})
        manager = _manager(
            _manifest(
                Resource(
                    kind="schedule",
                    name="nightly",
                    in_="application:api",
                    data={"name": "nightly", "cronExpression": "0 3 * * *", "command": "echo x"},
                )
            ),
            client,
            [_service("application", "api", "a1")],
        )
        manager.run()
        create = next(c for c in client.calls if c[1] == "schedule.create")
        assert create[2]["body"]["applicationId"] == "a1"

    def test_schedule_update_merges_live_fields(self):
        """We expect schedule updates to preserve fields the manifest omits."""
        client = FakeClient(
            {
                "application.one": {"applicationId": "a1"},
                "schedule.list": [
                    {
                        "scheduleId": "s1",
                        "name": "reorder-stalled",
                        "cronExpression": "*/5 * * * *",
                        "command": "bash /watcher/stalled-reorder.sh",
                        "enabled": True,
                        "serviceName": "qbittorrent",
                        "shellType": "bash",
                        "scheduleType": "compose",
                        "appName": "media-torrents",
                    }
                ],
            }
        )
        manager = _manager(
            _manifest(
                Resource(
                    kind="schedule",
                    name="reorder-stalled",
                    in_="application:api",
                    data={"name": "reorder-stalled", "cronExpression": "*/5 * * * *", "command": "echo changed"},
                )
            ),
            client,
            [_service("application", "api", "a1")],
        )
        manager.run()
        update = next(c for c in client.calls if c[1] == "schedule.update")
        body = update[2]["body"]
        assert body["scheduleId"] == "s1"
        assert body["command"] == "echo changed"
        assert body["serviceName"] == "qbittorrent"
        assert body["shellType"] == "bash"
        assert body["scheduleType"] == "compose"
        assert manager.report.actions[0].action == "update"

    def test_dry_run_plans_create(self):
        """We expect dry-run to record the action without calling the API."""
        client = FakeClient({"compose.one": {"composeId": "c1", "domains": []}})
        manager = _manager(
            _manifest(Resource(kind="domain", name="x.example.com", in_="compose:web", data={"host": "x.example.com"})),
            client,
            [_service("compose", "web", "c1")],
        )
        manager.run(dry_run=True)
        assert manager.report.actions[0].action == "create"
        assert not any(c[1] == "domain.create" for c in client.calls)

    def test_backup_resolves_destination_by_name(self):
        """We expect a backup destination to be resolved from destination.all."""
        client = FakeClient(
            {
                "postgres.one": {"postgresId": "pg1", "backups": []},
                "destination.all": [{"destinationId": "dst1", "name": "local-bucket"}],
            }
        )
        manager = _manager(
            _manifest(
                Resource(
                    kind="backup",
                    name="daily",
                    in_="postgres:db",
                    data={"destination": "local-bucket", "schedule": "0 3 * * *", "prefix": "db", "database": "db"},
                )
            ),
            client,
            [_service("postgres", "db", "pg1")],
        )
        manager.run()
        create = next(c for c in client.calls if c[1] == "backup.create")
        assert create[2]["body"]["destinationId"] == "dst1"
        assert "destination" not in create[2]["body"]
        assert create[2]["body"]["postgresId"] == "pg1"

    def test_backup_unknown_destination_raises(self):
        """We expect an unknown backup destination to abort."""
        client = FakeClient(
            {
                "postgres.one": {"postgresId": "pg1", "backups": []},
                "destination.all": [],
            }
        )
        manager = _manager(
            _manifest(
                Resource(
                    kind="backup",
                    name="daily",
                    in_="postgres:db",
                    data={"destination": "nope", "schedule": "0 3 * * *", "prefix": "db", "database": "db"},
                )
            ),
            client,
            [_service("postgres", "db", "pg1")],
        )
        with pytest.raises(ValueError):
            manager.run()

    def test_backup_update_merges_live_fields(self):
        """We expect backup updates to merge live fields the create may not set."""
        client = FakeClient(
            {
                "postgres.one": {
                    "postgresId": "pg1",
                    "backups": [
                        {
                            "backupId": "b1",
                            "schedule": "0 3 * * *",
                            "enabled": True,
                            "prefix": "db",
                            "destinationId": "dst1",
                            "database": "db",
                            "keepLatestCount": 7,
                            "serviceName": "db",
                            "metadata": None,
                        }
                    ],
                },
                "destination.all": [{"destinationId": "dst1", "name": "local-bucket"}],
            }
        )
        manager = _manager(
            _manifest(
                Resource(
                    kind="backup",
                    name="daily",
                    in_="postgres:db",
                    data={"destination": "local-bucket", "schedule": "0 3 * * *", "prefix": "db2", "database": "db"},
                )
            ),
            client,
            [_service("postgres", "db", "pg1")],
        )
        manager.run()
        update = next(c for c in client.calls if c[1] == "backup.update")
        body = update[2]["body"]
        assert body["prefix"] == "db2"
        assert body["enabled"] is True
        assert body["keepLatestCount"] == 7
        assert body["backupId"] == "b1"


def test_service_kinds_include_compose_application_and_dbs():
    """We expect the service kinds that can host leaf resources."""
    assert {"compose", "application", "postgres", "mysql", "redis"} <= SERVICE_KINDS
