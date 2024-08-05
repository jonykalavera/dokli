
"""Dokploy API

Endpoints for dokploy

The version of the OpenAPI document: v0.6.1
Generated by OpenAPI Generator (https://openapi-generator.tech)

Do not edit the class manually.
"""  # noqa: E501

import unittest

from openapi_client.models.mongo_start_request import MongoStartRequest


class TestMongoStartRequest(unittest.TestCase):
    """MongoStartRequest unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> MongoStartRequest:
        """Test MongoStartRequest
        include_optional is a boolean, when False only required
        params are included, when True both required and
        optional params are included
        """
        # uncomment below to create an instance of `MongoStartRequest`
        """
        model = MongoStartRequest()
        if include_optional:
            return MongoStartRequest(
                mongo_id = ''
            )
        else:
            return MongoStartRequest(
                mongo_id = '',
        )
        """

    def testMongoStartRequest(self):
        """Test MongoStartRequest"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)


if __name__ == "__main__":
    unittest.main()
