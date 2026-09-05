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


@pytest.fixture(autouse=True)
def _reset_icon_overrides():
    """Isolate the icons module's global color overrides between tests.

    ``DokliApp`` applies ``entity_colors``/``state_colors`` to module-level
    globals on construction and never resets them, so a test that builds an app
    with color overrides would otherwise leak them into the next test.
    """
    from dokli.tui.engine.icons import set_entity_color_overrides, set_state_color_overrides

    set_entity_color_overrides({})
    set_state_color_overrides({})
    yield
    set_entity_color_overrides({})
    set_state_color_overrides({})
