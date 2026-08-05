"""Formatting/redaction tests."""

from dokli.formatting import redact_secrets


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
