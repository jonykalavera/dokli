"""Secrets stored in the OS keychain via :mod:`keyring`.

Deterministic account names (service ``dokli``):

- ``conn.<name>`` — API key of a connection.
- ``provider.<name>`` — git provider credential.
- ``db.<name>`` — database password.

Resolution order used by the models is: literal value in the config/manifest,
then the keychain, then ``*_cmd``. Storing a secret in the keychain keeps it
out of the YAML files.
"""

import contextlib

import keyring
from keyring import errors

SERVICE = "dokli"


def set_secret(account: str, value: str) -> None:
    """Store a secret under an account name."""
    keyring.set_password(SERVICE, account, value)


def get_secret(account: str) -> str | None:
    """Return a stored secret, or ``None`` if it does not exist."""
    return keyring.get_password(SERVICE, account)


def delete_secret(account: str) -> None:
    """Remove a stored secret, ignoring missing accounts."""
    with contextlib.suppress(errors.PasswordDeleteError):
        keyring.delete_password(SERVICE, account)


def conn_account(name: str) -> str:
    """Keychain account for a connection's API key."""
    return f"conn.{name}"


def provider_account(name: str) -> str:
    """Keychain account for a git provider's credential."""
    return f"provider.{name}"


def db_account(name: str) -> str:
    """Keychain account for a database service's password."""
    return f"db.{name}"
