
"""Dokploy API

Endpoints for dokploy

The version of the OpenAPI document: v0.6.1
Generated by OpenAPI Generator (https://openapi-generator.tech)

Do not edit the class manually.
"""  # noqa: E501

import unittest

from openapi_client.models.port_delete_request import PortDeleteRequest


class TestPortDeleteRequest(unittest.TestCase):
    """PortDeleteRequest unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> PortDeleteRequest:
        """Test PortDeleteRequest
        include_optional is a boolean, when False only required
        params are included, when True both required and
        optional params are included
        """
        # uncomment below to create an instance of `PortDeleteRequest`
        """
        model = PortDeleteRequest()
        if include_optional:
            return PortDeleteRequest(
                port_id = '0'
            )
        else:
            return PortDeleteRequest(
                port_id = '0',
        )
        """

    def testPortDeleteRequest(self):
        """Test PortDeleteRequest"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)


if __name__ == "__main__":
    unittest.main()