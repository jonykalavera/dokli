"""Config tests."""

import pytest
from polyfactory.factories.pydantic_factory import ModelFactory
from pydantic import ValidationError

from dokli.config import Config, ConnectionConfig


class ConnectionConfigFactory(ModelFactory[ConnectionConfig]):
    """Connection factory."""

    api_key = None
    api_key_cmd = "echo 'my api key from cmd'"


class ConfigFactory(ModelFactory[Config]):
    """Config factory."""

    connections = [ConnectionConfigFactory.build()]


class TestConfig:
    """Config model tests."""

    def test_config(self):
        """We expect to be able to declare an api with connections."""
        config = ConfigFactory.build()
        assert config.connections

    def test_get_connection(self):
        """We expect to be able to get a connection by name."""
        connection = ConnectionConfigFactory.build(name="dokploy")
        config = ConfigFactory.build(connections=[connection])
        assert config.get_connection("dokploy")


class TestConnectionConfig:
    """Connection config model tests."""

    def test_must_provide_api_key_or_cmd(self):
        """We expect to raise an error if no api key or cmd is provided."""
        with pytest.raises(ValidationError):
            ConnectionConfig(name="dokli", url="https://dokli.example.com")

    def test_connection_with_api_key(self):
        """We expect to be able to declare a connection with an API key."""
        config = ConnectionConfigFactory.build(api_key="*" * 40)
        assert config.get_api_key() == config.api_key.get_secret_value()

    def test_connection_with_api_key_cmd(self, mocker):
        """We expect to be able to declare a connection with an API key command."""
        config = ConnectionConfigFactory.build()
        assert config.api_key is None
        check_output = mocker.patch("dokli.config.subprocess.check_output", return_value=b"my api key from cmd")
        assert config.get_api_key() == "my api key from cmd"
        check_output.assert_called_once_with(config.api_key_cmd.split())

    def test_model_dump_clear_prints_clear_secrets(self):
        """We expect to be able to dump the config with clear secrets."""
        config = ConnectionConfigFactory.build(api_key="*" * 40)
        result = config.model_dump_clear()
        assert result["api_key"] == "*" * 40
