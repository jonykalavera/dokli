
"""Dokploy API

Endpoints for dokploy

The version of the OpenAPI document: v0.6.1
Generated by OpenAPI Generator (https://openapi-generator.tech)

Do not edit the class manually.
"""  # noqa: E501

import unittest

from openapi_client.models.destination_create_request import DestinationCreateRequest


class TestDestinationCreateRequest(unittest.TestCase):
    """DestinationCreateRequest unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> DestinationCreateRequest:
        """Test DestinationCreateRequest
        include_optional is a boolean, when False only required
        params are included, when True both required and
        optional params are included
        """
        # uncomment below to create an instance of `DestinationCreateRequest`
        """
        model = DestinationCreateRequest()
        if include_optional:
            return DestinationCreateRequest(
                name = '0',
                access_key = '',
                bucket = '',
                region = '',
                endpoint = '',
                secret_access_key = ''
            )
        else:
            return DestinationCreateRequest(
                name = '0',
                access_key = '',
                bucket = '',
                region = '',
                endpoint = '',
                secret_access_key = '',
        )
        """

    def testDestinationCreateRequest(self):
        """Test DestinationCreateRequest"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)


if __name__ == "__main__":
    unittest.main()
