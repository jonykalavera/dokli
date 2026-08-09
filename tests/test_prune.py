"""Prune tests (issue #49)."""

from dokli.manifest import ApplicationService, ComposeService, Manifest, ProjectDef, Resource
from dokli.report import ApplyReport
from dokli.prune import Pruner

SPECS = {
    "domain": ("domain.delete", "domainId", {}),
    "application": ("application.delete", "applicationId", {}),
    "compose": ("compose.delete", "composeId", {"deleteVolumes": False}),
}


def _service(kind, name, service_id):
    return type("S", (), {"type": kind, "name": name, "service_id": service_id})()


def _service_def(kind, name):
    if kind == "compose":
        return ComposeService(name=name)
    return ApplicationService(name=name)


def _project(name, *services):
    project = type(
        "P",
        (),
        {
            "name": name,
            "environments": [
                type(
                    "E",
                    (),
                    {"name": "", "is_default": True, "environment_id": "e1", "services": list(services)},
                )()
            ],
        },
    )()
    return project


def _state(*projects):
    return type("S", (), {"projects": list(projects)})()


class FakeClient:
    def __init__(self, records=None):
        self.calls = []
        self.records = records or {}

    def request(self, method, path, params):
        self.calls.append((method, path, params))
        records = self.records

        class _Response:
            def json(self):
                return records.get(path, {})

        return _Response()


def _pruner(manifest, client, state, mocker):
    mocker.patch("dokli.prune.delete_spec", side_effect=lambda registry, kind: SPECS.get(kind))
    applier = type("A", (), {})()
    applier.manifest = manifest
    applier.client = client
    applier.report = ApplyReport()
    applier._state = state
    return Pruner(applier, {})


def _manifest(*projects, resources=()):
    return Manifest(connection="test", projects=list(projects), resources=list(resources))


class TestPruner:
    """Destructive reconciliation."""

    def test_prunes_unmanaged_service(self, mocker):
        """We expect services not in the manifest to be deleted."""
        client = FakeClient({})
        state = _state(_project("app", _service("application", "web", "a1"), _service("application", "legacy", "a2")))
        project = ProjectDef(name="app", services=[_service_def("application", "web")])
        pruner = _pruner(_manifest(project), client, state, mocker)

        pruner.run()

        deletes = [a for a in pruner.report.actions if a.action == "delete"]
        assert [d.name for d in deletes] == ["legacy"]
        assert ("POST", "application.delete", {"body": {"applicationId": "a2"}}) in client.calls

    def test_prunes_unmanaged_children(self, mocker):
        """We expect child records not in the manifest to be deleted."""
        client = FakeClient(
            {
                "compose.one": {
                    "composeId": "c1",
                    "domains": [
                        {"domainId": "d1", "host": "keep.example.com"},
                        {"domainId": "d2", "host": "drop.example.com"},
                    ],
                }
            }
        )
        state = _state(_project("app", _service("compose", "backend", "c1")))
        project = ProjectDef(name="app", services=[_service_def("compose", "backend")])
        resource = Resource(
            kind="domain", name="keep.example.com", in_="compose:backend", data={"host": "keep.example.com"}
        )
        pruner = _pruner(_manifest(project, resources=[resource]), client, state, mocker)

        pruner.run()

        deletes = [a for a in pruner.report.actions if a.action == "delete"]
        assert [d.name for d in deletes] == ["drop.example.com"]
        assert ("POST", "domain.delete", {"body": {"domainId": "d2"}}) in client.calls

    def test_compose_delete_includes_defaults(self, mocker):
        """We expect required delete defaults (deleteVolumes) to be sent."""
        client = FakeClient({})
        state = _state(_project("app", _service("compose", "legacy", "c1")))
        project = ProjectDef(name="app", services=[])
        pruner = _pruner(_manifest(project), client, state, mocker)

        pruner.run()

        assert ("POST", "compose.delete", {"body": {"composeId": "c1", "deleteVolumes": False}}) in client.calls

    def test_leaves_undeclared_projects(self, mocker):
        """We expect projects not in the manifest to be untouched."""
        client = FakeClient({})
        state = _state(
            _project("app", _service("application", "web", "a1")),
            _project("other", _service("application", "web", "a9")),
        )
        project = ProjectDef(name="app", services=[_service_def("application", "web")])
        pruner = _pruner(_manifest(project), client, state, mocker)

        pruner.run()

        assert not any(a.action == "delete" for a in pruner.report.actions)

    def test_dry_run_records_without_calling(self, mocker):
        """We expect dry-run to record deletes without calling the API."""
        client = FakeClient({})
        state = _state(_project("app", _service("application", "legacy", "a2")))
        project = ProjectDef(name="app", services=[])
        pruner = _pruner(_manifest(project), client, state, mocker)

        pruner.run(dry_run=True)

        assert [a.action for a in pruner.report.actions] == ["delete"]
        assert not any("application.delete" in c[1] for c in client.calls)
