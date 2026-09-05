"""Formatting/redaction tests."""

import json

from dokli.formatting import (
    Format,
    _format_agent,
    _flatten_record,
    format_data,
    is_secret_field,
    redact_secrets,
    redact_secrets_counted,
    select_fields,
)


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

    def test_masks_all_env_values_by_default(self):
        """We expect every env value to be masked by default, regardless of key."""
        data = {"env": "NODE_ENV=production\nDB_PASSWORD=hunter2\nAPI_KEY=abc123\nPATH=/usr/bin"}
        redacted = redact_secrets(data)
        assert redacted["env"] == "NODE_ENV=***\nDB_PASSWORD=***\nAPI_KEY=***\nPATH=***"

    def test_env_keys_stay_visible(self):
        """We expect the env key names to remain visible when their values are masked."""
        redacted = redact_secrets({"env": "GH_PAT=github_pat_abc\nREDIS_PASS=hunter2"})
        assert redacted["env"] == "GH_PAT=***\nREDIS_PASS=***"

    def test_reveals_only_requested_env_keys(self):
        """We expect --show-env to keep only the listed values in plain text."""
        data = {"env": "GH_PAT=github_pat_abc\nNODE_ENV=prod\nPORT=3000"}
        redacted, count = redact_secrets_counted(data, reveal_env=frozenset({"NODE_ENV", "PORT"}))
        assert redacted["env"] == "GH_PAT=***\nNODE_ENV=prod\nPORT=3000"
        assert count == 1

    def test_masks_pem_continuation_lines(self):
        """We expect a masked multi-line value (PEM) to mask its continuation lines too."""
        data = {"env": "CERT=-----BEGIN RSA PRIVATE KEY-----\nabc\n-----END RSA PRIVATE KEY-----"}
        redacted = redact_secrets(data)
        assert redacted["env"] == "CERT=***\n***\n***"

    def test_short_words_do_not_overmatch(self):
        """We expect standalone-only matching to leave PASS/KEY/PAT substrings alone."""
        data = {"compass": 1, "hockey": 2, "path": "/usr", "bypass": "no"}
        assert redact_secrets(data) == data

    def test_redact_secrets_counted(self):
        """We expect the counted variant to report the number of masked values."""
        data = {"name": "app", "databasePassword": "hunter2", "env": "GH_PAT=github_pat_abc\nNODE_ENV=prod"}
        redacted, count = redact_secrets_counted(data)
        assert count == 3
        assert redacted["databasePassword"] == "***"
        assert redacted["env"] == "GH_PAT=***\nNODE_ENV=***"

    def test_counted_ignores_none_secret_values(self):
        """We expect None secret fields not to count as masked."""
        redacted, count = redact_secrets_counted({"databasePassword": None})
        assert redacted == {"databasePassword": None}
        assert count == 0

    def test_unrelated_fields_untouched(self):
        """We expect unrelated fields to pass through unchanged."""
        data = {"projectId": "p1", "name": "app", "services": []}
        assert redact_secrets(data) == data

    def test_masks_env_like_blobs(self):
        """We expect previewEnv and envVariables to be masked like env."""
        data = {"previewEnv": "GH_PAT=x\nPUBLIC_URL=y", "envVariables": "DB_URL=z\nNODE_ENV=prod"}
        redacted = redact_secrets(data)
        assert redacted["previewEnv"] == "GH_PAT=***\nPUBLIC_URL=***"
        assert redacted["envVariables"] == "DB_URL=***\nNODE_ENV=***"

    def test_reveal_env_applies_to_env_like_blobs(self):
        """We expect --show-env to reveal keys in previewEnv too."""
        data = {"previewEnv": "GH_PAT=x\nPUBLIC_URL=y"}
        redacted, count = redact_secrets_counted(data, reveal_env=frozenset({"PUBLIC_URL"}))
        assert redacted["previewEnv"] == "GH_PAT=***\nPUBLIC_URL=y"
        assert count == 1

    def test_masks_opaque_secret_blobs(self):
        """We expect content/metadata/buildArgs to be masked whole."""
        data = {
            "content": "s3://access:secret@bucket",
            "metadata": {"accessKey": "x", "region": "us"},
            "buildArgs": "NPM_TOKEN=x\nBASE=node",
            "previewBuildArgs": "NPM_TOKEN=y",
        }
        redacted = redact_secrets(data)
        assert redacted["content"] == "***"
        assert redacted["metadata"] == "***"
        assert redacted["buildArgs"] == "***"
        assert redacted["previewBuildArgs"] == "***"

    def test_leaves_inspectable_blobs_visible(self):
        """We expect composeFile/dockerCompose/script to stay visible by default."""
        data = {"composeFile": "services:\n  web: {}", "dockerCompose": "x", "script": "echo hi"}
        assert redact_secrets(data) == data

    def test_leaves_create_env_file_flag_visible(self):
        """We expect the boolean createEnvFile flag not to be masked."""
        assert redact_secrets({"createEnvFile": True}) == {"createEnvFile": True}

    def test_does_not_mask_booleans_and_numbers(self):
        """We expect flags/counts not to be masked: they carry no secret material."""
        data = {"forwardAuthEnabled": True, "includeEncryptionKey": False, "keyCount": 3}
        redacted, count = redact_secrets_counted(data)
        assert redacted == data
        assert count == 0

    def test_does_not_mask_empty_values(self):
        """We expect empty secret fields to stay empty, not to imply a secret is set."""
        redacted, count = redact_secrets_counted({"password": "", "apiKey": None})
        assert redacted == {"password": "", "apiKey": None}
        assert count == 0

    def test_is_secret_field_matches_redactor(self):
        """We expect the predicate to agree with what the redactor actually masks."""
        probe = "K=v"
        names = [
            "name",
            "projectId",
            "composeFile",
            "databasePassword",
            "refreshToken",
            "apiKey",
            "env",
            "previewEnv",
            "envVariables",
            "content",
            "metadata",
            "buildArgs",
        ]
        for name in names:
            changed = redact_secrets({name: probe})[name] != probe
            assert changed == is_secret_field(name), name

    def test_export_secret_fields_are_masked_by_display(self):
        """We expect every export-secret field to be covered by the display predicate.

        Guards against the export secret maps and the display redaction drifting
        apart (issue #138).
        """
        from dokli.resources import SECRET_FIELDS, SECRET_OPT_FIELDS

        for fields in (*SECRET_FIELDS.values(), *SECRET_OPT_FIELDS.values()):
            for field in fields:
                assert is_secret_field(field), f"field {field!r} is export-secret but not display-masked"


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
