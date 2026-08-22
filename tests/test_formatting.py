"""Formatting/redaction tests."""

import json

from dokli.formatting import Format, _format_agent, _flatten_record, format_data, redact_secrets, select_fields


class TestRedactSecrets:
    """Secret redaction tests."""

    def test_redacts_secret_keys(self):
        """We expect secret-like keys to be redacted."""
        data = {"name": "myapp", "databasePassword": "hunter2", "refreshToken": "abc"}
        redacted = redact_secrets(data)
        assert redacted["databasePassword"] == "***"
        assert redacted["refreshToken"] == "***"
        assert redacted["name"] == "myapp"

    def test_keeps_none_values(self):
        """We expect None values to stay None."""
        assert redact_secrets({"password": None}) == {"password": None}

    def test_redacts_nested_lists(self):
        """We expect redaction to recurse into lists."""
        data = {"items": [{"token": "x"}, {"name": "ok"}]}
        assert redact_secrets(data) == {"items": [{"token": "***"}, {"name": "ok"}]}

    def test_redacts_env_variables(self):
        """We expect secret-like variables in env to be redacted by value."""
        data = {"env": "NODE_ENV=production\nDB_PASSWORD=hunter2\nAPI_KEY=abc123"}
        redacted = redact_secrets(data)
        assert redacted["env"] == "NODE_ENV=production\nDB_PASSWORD=***\nAPI_KEY=***"

    def test_unrelated_fields_untouched(self):
        """We expect unrelated fields to pass through unchanged."""
        data = {"projectId": "p1", "name": "app", "services": []}
        assert redact_secrets(data) == data


class TestFormatData:
    """JSON/yaml formatting."""

    def test_json_escapes_newlines(self):
        """We expect json output to keep newlines escaped and stay parseable."""
        data = {"name": "web", "env": "A=1\nB=2\nTOKEN=secret"}
        out = format_data(data, Format.json)
        assert "\n" not in out.replace("\\n", "")
        assert json.loads(out) == data

    def test_json_indent(self):
        """We expect --indent to pretty-print json (still parseable)."""
        data = {"env": "A=1\nB=2"}
        out = format_data(data, Format.json, indent=2)
        assert json.loads(out) == data
        assert "\n  " in out


class TestSelectFields:
    """Top-level field selection (jq-like)."""

    def test_keeps_only_requested_fields(self):
        """We expect only the requested top-level keys to remain."""
        data = {"id": "p1", "name": "web", "description": "x"}
        assert select_fields(data, ["id", "name"]) == {"id": "p1", "name": "web"}

    def test_drops_unknown_fields(self):
        """We expect unknown field names to be dropped."""
        assert select_fields({"a": 1, "b": 2}, ["b", "nope"]) == {"b": 2}

    def test_empty_fields_returns_data(self):
        """We expect fields=[] to return the data unchanged."""
        data = {"a": 1, "b": 2}
        assert select_fields(data, []) is data

    def test_filters_each_list_record(self):
        """We expect a list of dicts to filter each record."""
        rows = [{"a": 1, "b": "x"}, {"a": 2, "b": "y"}]
        assert select_fields(rows, ["a"]) == [{"a": 1}, {"a": 2}]

    def test_scalars_pass_through(self):
        """We expect scalars and lists of scalars to be untouched."""
        assert select_fields("hello", ["a"]) == "hello"
        assert select_fields([1, 2], ["a"]) == [1, 2]

    def test_none_values_filtered_in(self):
        """We expect present keys with None values to stay."""
        assert select_fields({"a": None, "b": 1}, ["a"]) == {"a": None}


class TestFormatAgent:
    """NDJSON dataframe serialization (header + rows)."""

    def test_flatten_record_nested(self):
        """We expect nested dicts to flatten with __ separators."""
        flat = _flatten_record({"network": {"down": 1.0, "up": 2.0}, "cpu": 0.5})
        assert flat == {"network__down": 1.0, "network__up": 2.0, "cpu": 0.5}

    def test_agent_list_of_dicts(self):
        """We expect a list to become a header row + one row per record."""
        out = _format_agent([{"a": 1, "b": "x"}, {"a": 2, "b": "y"}])
        lines = out.strip().split("\n")
        assert json.loads(lines[0]) == ["a", "b"]
        assert json.loads(lines[1]) == [1, "x"]
        assert json.loads(lines[2]) == [2, "y"]

    def test_agent_single_dict(self):
        """We expect a single dict to become a header + one row."""
        out = _format_agent({"cpu": 0.5, "disk": None})
        lines = out.strip().split("\n")
        assert json.loads(lines[0]) == ["cpu", "disk"]
        assert json.loads(lines[1]) == [0.5, None]

    def test_agent_is_parseable_line_by_line(self):
        """We expect every line (header and rows) to be valid JSON."""
        out = format_data([{"a": 1}, {"a": 2}], Format.agent)
        for line in out.strip().split("\n"):
            json.loads(line)
