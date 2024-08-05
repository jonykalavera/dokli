
"""Dokploy API

Endpoints for dokploy

The version of the OpenAPI document: v0.6.1
Generated by OpenAPI Generator (https://openapi-generator.tech)

Do not edit the class manually.
"""  # noqa: E501

import unittest

from openapi_client.api.redis_api import RedisApi


class TestRedisApi(unittest.TestCase):
    """RedisApi unit test stubs"""

    def setUp(self) -> None:
        self.api = RedisApi()

    def tearDown(self) -> None:
        pass

    def test_redis_change_status(self) -> None:
        """Test case for redis_change_status"""
        pass

    def test_redis_create(self) -> None:
        """Test case for redis_create"""
        pass

    def test_redis_deploy(self) -> None:
        """Test case for redis_deploy"""
        pass

    def test_redis_one(self) -> None:
        """Test case for redis_one"""
        pass

    def test_redis_reload(self) -> None:
        """Test case for redis_reload"""
        pass

    def test_redis_remove(self) -> None:
        """Test case for redis_remove"""
        pass

    def test_redis_save_environment(self) -> None:
        """Test case for redis_save_environment"""
        pass

    def test_redis_save_external_port(self) -> None:
        """Test case for redis_save_external_port"""
        pass

    def test_redis_start(self) -> None:
        """Test case for redis_start"""
        pass

    def test_redis_stop(self) -> None:
        """Test case for redis_stop"""
        pass

    def test_redis_update(self) -> None:
        """Test case for redis_update"""
        pass


if __name__ == "__main__":
    unittest.main()
