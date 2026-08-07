"""Keychain secrets tests (issue #48)."""

import typer
from typer.testing import CliRunner

from dokli.secrets import SERVICE, conn_account, db_account, delete_secret, get_secret, provider_account, set_secret
from dokli.secrets_cli import _mask, build_command

runner = CliRunner()


def _app():
    app = typer.Typer()
    app.add_typer(build_command())
    return app


class TestSecrets:
    """Keychain wrapper tests."""

    def test_set_get_delete(self, fake_keyring):
        """We expect a secret to round-trip through the keychain."""
        set_secret(conn_account("meche"), "*" * 64)
        assert get_secret(conn_account("meche")) == "*" * 64
        delete_secret(conn_account("meche"))
        assert get_secret(conn_account("meche")) is None

    def test_delete_missing_is_noop(self, fake_keyring):
        """We expect deleting an absent secret not to raise."""
        delete_secret(conn_account("nope"))

    def test_account_names(self):
        """We expect deterministic account names."""
        assert conn_account("meche") == "conn.meche"
        assert provider_account("github-main") == "provider.github-main"
        assert db_account("backend") == "db.backend"


class TestSecretsCLI:
    """dokli secrets command tests."""

    def test_set_get_rm(self, fake_keyring):
        """We expect the CLI to store, read and remove a secret."""
        result = runner.invoke(
            _app(), ["secrets", "set", "conn.meche", "--stdin"], input="*" * 64 + "\n"
        )
        assert result.exit_code == 0
        assert fake_keyring.store[("dokli", "conn.meche")] == "*" * 64

        result = runner.invoke(_app(), ["secrets", "get", "conn.meche"])
        assert result.exit_code == 0
        assert "*" * 64 not in result.output
        assert "***" in result.output or "…" in result.output

        result = runner.invoke(_app(), ["secrets", "get", "conn.meche", "--show"])
        assert result.exit_code == 0
        assert "*" * 64 in result.output

        result = runner.invoke(_app(), ["secrets", "rm", "conn.meche"])
        assert result.exit_code == 0
        assert ("dokli", "conn.meche") not in fake_keyring.store

    def test_get_missing_fails(self, fake_keyring):
        """We expect get on an absent secret to fail with a non-zero exit."""
        result = runner.invoke(_app(), ["secrets", "get", "conn.nope"])
        assert result.exit_code == 1


def test_mask():
    """We expect the value to be masked, keeping only the edges."""
    assert _mask("*" * 64) == "****…****"
    assert _mask("short") == "***"
