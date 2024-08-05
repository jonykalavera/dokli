
"""Dokploy API

Endpoints for dokploy

The version of the OpenAPI document: v0.6.1
Generated by OpenAPI Generator (https://openapi-generator.tech)

Do not edit the class manually.
"""  # noqa: E501

import unittest

from openapi_client.api.mariadb_api import MariadbApi


class TestMariadbApi(unittest.TestCase):
    """MariadbApi unit test stubs"""

    def setUp(self) -> None:
        self.api = MariadbApi()

    def tearDown(self) -> None:
        pass

    def test_mariadb_change_status(self) -> None:
        """Test case for mariadb_change_status"""
        pass

    def test_mariadb_create(self) -> None:
        """Test case for mariadb_create"""
        pass

    def test_mariadb_deploy(self) -> None:
        """Test case for mariadb_deploy"""
        pass

    def test_mariadb_one(self) -> None:
        """Test case for mariadb_one"""
        pass

    def test_mariadb_reload(self) -> None:
        """Test case for mariadb_reload"""
        pass

    def test_mariadb_remove(self) -> None:
        """Test case for mariadb_remove"""
        pass

    def test_mariadb_save_environment(self) -> None:
        """Test case for mariadb_save_environment"""
        pass

    def test_mariadb_save_external_port(self) -> None:
        """Test case for mariadb_save_external_port"""
        pass

    def test_mariadb_start(self) -> None:
        """Test case for mariadb_start"""
        pass

    def test_mariadb_stop(self) -> None:
        """Test case for mariadb_stop"""
        pass

    def test_mariadb_update(self) -> None:
        """Test case for mariadb_update"""
        pass


if __name__ == "__main__":
    unittest.main()