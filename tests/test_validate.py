"""Offline manifest validation tests (issue #50)."""

from dokli.config import ConnectionConfig
from dokli.manifest import Manifest, Resource
from dokli.validate import validate_manifest

SCHEMA = {
    "paths": {
        "/compose.one": {
            "get": {"parameters": [{"name": "composeId", "in": "query", "required": True}]}
        },
        "/domain.create": {
            "post": {
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {"host": {"type": "string"}, "composeId": {"type": "string"}},
                                "required": ["host"],
                            }
                        }
                    }
                }
            }
        },
        "/domain.update": {
            "post": {
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {"domainId": {"type": "string"}, "host": {"type": "string"}},
                            }
                        }
                    }
                }
            }
        },
    }
}


def _connection(mocker) -> ConnectionConfig:
    connection = ConnectionConfig(name="test-env", url="https://example.com", api_key_cmd="echo key")
    mocker.patch("dokli.validate.APIClient", return_value=type("C", (), {"schema": SCHEMA})())
    return connection


def _manifest(*resources) -> Manifest:
    return Manifest(connection="test", resources=list(resources))


def test_valid_manifest(mocker):
    """We expect a valid resource to produce no issues."""
    manifest = _manifest(
        Resource(kind="domain", name="x.example.com", in_="compose:web", data={"host": "x.example.com"})
    )
    assert validate_manifest(_connection(mocker), manifest) == []


def test_unknown_kind(mocker):
    """We expect an unknown kind to be flagged."""
    manifest = _manifest(Resource(kind="nope", name="x", in_="compose:web", data={}))
    issues = validate_manifest(_connection(mocker), manifest)
    assert any("unknown kind" in issue for issue in issues)


def test_unknown_field(mocker):
    """We expect a field absent from the schema to be flagged."""
    manifest = _manifest(Resource(kind="domain", name="x", in_="compose:web", data={"bogus": 1}))
    issues = validate_manifest(_connection(mocker), manifest)
    assert any("unknown field 'bogus'" in issue for issue in issues)


def test_missing_in(mocker):
    """We expect a resource without a parent to be flagged."""
    manifest = _manifest(Resource(kind="domain", name="x", data={"host": "x"}))
    issues = validate_manifest(_connection(mocker), manifest)
    assert any("missing 'in:'" in issue for issue in issues)


def test_unsupported_parent(mocker):
    """We expect a non-service parent to be flagged."""
    manifest = _manifest(Resource(kind="domain", name="x", in_="project:media", data={"host": "x"}))
    issues = validate_manifest(_connection(mocker), manifest)
    assert any("not supported yet" in issue for issue in issues)
