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

    def test_parent_not_found(self):
        """We expect an error when the parent service is not in the instance."""
        client = FakeClient({})
        manager = _manager(
            _manifest(Resource(kind="domain", name="x.example.com", in_="compose:nope", data={"host": "x.example.com"})),
            client,
            [],
        )
        with pytest.raises(ValueError):
            manager.run()

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
        """We expect mounts to address their parent via serviceId + serviceType."""
        client = FakeClient({"compose.one": {"composeId": "c1", "mounts": []}})
        manager = _manager(
            _manifest(
                Resource(kind="mount", name="rclone.conf", in_="compose:web", data={"filePath": "rclone.conf", "mountPath": "/"})
            ),
            client,
            [_service("compose", "web", "c1")],
        )
        manager.run()
        create = next(c for c in client.calls if c[1] == "mount.create")
        body = create[2]["body"]
        assert body["serviceId"] == "c1"
        assert body["serviceType"] == "compose"

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


def test_service_kinds_include_compose_application_and_dbs():
    """We expect the service kinds that can host leaf resources."""
    assert {"compose", "application", "postgres", "mysql", "redis"} <= SERVICE_KINDS
