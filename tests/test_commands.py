"""Dokli command tests."""

import json

import pytest

from dokli.commands import MAGIC_FILE, MAGIC_JSON, _parse_params


class TestParseParams:
    """CLI param parsing tests."""

    def test_passes_typed_values_through(self):
        """We expect schema-typed params (int, bool, float) to pass untouched."""
        parsed = _parse_params({"tail": 20, "force": True, "ratio": 0.5, "name": "web"})
        assert parsed == {"tail": 20, "force": True, "ratio": 0.5, "name": "web"}

    def test_decodes_json_magic(self):
        """We expect the %json: prefix to decode structured values."""
        parsed = _parse_params({"env": f"{MAGIC_JSON}{json.dumps({'A': '1'})}"})
        assert parsed == {"env": {"A": "1"}}

    def test_decodes_file_magic(self, tmp_path):
        """We expect the %file: prefix to load a JSON file."""
        payload = {"image": "nginx", "tag": "latest"}
        path = tmp_path / "payload.json"
        path.write_text(json.dumps(payload))
        parsed = _parse_params({"body": f"{MAGIC_FILE}{path}"})
        assert parsed == {"body": payload}

    def test_plain_string_unchanged(self):
        """We expect an ordinary string to pass through unchanged."""
        assert _parse_params({"env": "PORT=8080"}) == {"env": "PORT=8080"}

    def test_drops_none_and_empty_values(self):
        """We expect unset and empty params to be dropped, not sent empty."""
        assert _parse_params({"serverId": "", "tail": None, "appName": "media"}) == {"appName": "media"}
