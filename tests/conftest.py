"""Shared pytest fixtures."""

import keyring.core
import pytest
from keyring.backend import KeyringBackend


class FakeKeyring(KeyringBackend):
    """In-memory keyring backend for tests."""

    priority = 10

    def __init__(self) -> None:
        self.store: dict[tuple[str, str], str] = {}

    def set_password(self, service: str, username: str, password: str) -> None:
        self.store[(service, username)] = password

    def get_password(self, service: str, username: str) -> str | None:
        return self.store.get((service, username))

    def delete_password(self, service: str, username: str) -> None:
        self.store.pop((service, username), None)


@pytest.fixture()
def fake_keyring(monkeypatch):
    """Point keyring at an in-memory backend."""
    fake = FakeKeyring()
    monkeypatch.setattr(keyring.core, "_keyring_backend", fake)
    return fake
