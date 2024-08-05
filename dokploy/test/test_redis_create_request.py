
"""Dokploy API

Endpoints for dokploy

The version of the OpenAPI document: v0.6.1
Generated by OpenAPI Generator (https://openapi-generator.tech)

Do not edit the class manually.
"""  # noqa: E501

import unittest

from openapi_client.models.redis_create_request import RedisCreateRequest


class TestRedisCreateRequest(unittest.TestCase):
    """RedisCreateRequest unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> RedisCreateRequest:
        """Test RedisCreateRequest
        include_optional is a boolean, when False only required
        params are included, when True both required and
        optional params are included
        """
        # uncomment below to create an instance of `RedisCreateRequest`
        """
        model = RedisCreateRequest()
        if include_optional:
            return RedisCreateRequest(
                name = '0',
                app_name = '0',
                database_password = '',
                docker_image = 'redis:8',
                project_id = '',
                description = ''
            )
        else:
            return RedisCreateRequest(
                name = '0',
                app_name = '0',
                database_password = '',
                project_id = '',
        )
        """

    def testRedisCreateRequest(self):
        """Test RedisCreateRequest"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)


if __name__ == "__main__":
    unittest.main()