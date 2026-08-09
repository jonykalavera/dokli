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
        "/mounts.create": {
            "post": {
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "type": {"type": "string", "enum": ["bind", "volume", "file"]},
                                    "filePath": {"type": "string"},
                                    "mountPath": {"type": "string"},
                                },
                                "required": ["type", "filePath", "mountPath"],
                            }
                        }
                    }
                }
            }
        },
        "/mounts.update": {
            "post": {
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {"mountId": {"type": "string"}, "filePath": {"type": "string"}},
                            }
                        }
                    }
                }
            }
        },
        "/port.create": {
            "post": {
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {"publishedPort": {"type": "number"}},
                                "required": ["publishedPort"],
                            }
                        }
                    }
                }
            }
        },
        "/port.update": {
            "post": {
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {"portId": {"type": "string"}, "publishedPort": {"type": "number"}},
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


def test_wrong_service_parent(mocker):
    """We expect a port under a compose to be flagged (application-only)."""
    manifest = _manifest(Resource(kind="port", name="8080", in_="compose:web", data={"publishedPort": 8080}))
    issues = validate_manifest(_connection(mocker), manifest)
    assert any("cannot hang off 'compose'" in issue for issue in issues)


def test_mount_kind_valid(mocker):
    """We expect the mount kind to resolve to the mounts entity."""
    manifest = _manifest(
        Resource(
            kind="mount",
            name="rclone.conf",
            in_="compose:web",
            data={"type": "bind", "filePath": "rclone.conf", "mountPath": "/"},
        )
    )
    assert validate_manifest(_connection(mocker), manifest) == []


def test_mount_missing_required_type(mocker):
    """We expect a mount without its required type field to be flagged."""
    manifest = _manifest(
        Resource(kind="mount", name="rclone.conf", in_="compose:web", data={"filePath": "rclone.conf", "mountPath": "/"})
    )
    issues = validate_manifest(_connection(mocker), manifest)
    assert any("missing required field 'type'" in issue for issue in issues)
