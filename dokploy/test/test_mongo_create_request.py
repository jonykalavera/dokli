
"""Dokploy API

Endpoints for dokploy

The version of the OpenAPI document: v0.6.1
Generated by OpenAPI Generator (https://openapi-generator.tech)

Do not edit the class manually.
"""  # noqa: E501

import unittest

from openapi_client.models.mongo_create_request import MongoCreateRequest


class TestMongoCreateRequest(unittest.TestCase):
    """MongoCreateRequest unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> MongoCreateRequest:
        """Test MongoCreateRequest
        include_optional is a boolean, when False only required
        params are included, when True both required and
        optional params are included
        """
        # uncomment below to create an instance of `MongoCreateRequest`
        """
        model = MongoCreateRequest()
        if include_optional:
            return MongoCreateRequest(
                name = '0',
                app_name = '0',
                docker_image = 'mongo:15',
                project_id = '',
                description = '',
                database_user = '0',
                database_password = ''
            )
        else:
            return MongoCreateRequest(
                name = '0',
                app_name = '0',
                project_id = '',
                database_user = '0',
                database_password = '',
        )
        """

    def testMongoCreateRequest(self):
        """Test MongoCreateRequest"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)


if __name__ == "__main__":
    unittest.main()
