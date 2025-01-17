
"""Dokploy API

Endpoints for dokploy

The version of the OpenAPI document: v0.6.1
Generated by OpenAPI Generator (https://openapi-generator.tech)

Do not edit the class manually.
"""  # noqa: E501

import unittest

from openapi_client.models.port_create_request import PortCreateRequest


class TestPortCreateRequest(unittest.TestCase):
    """PortCreateRequest unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> PortCreateRequest:
        """Test PortCreateRequest
        include_optional is a boolean, when False only required
        params are included, when True both required and
        optional params are included
        """
        # uncomment below to create an instance of `PortCreateRequest`
        """
        model = PortCreateRequest()
        if include_optional:
            return PortCreateRequest(
                published_port = 1.337,
                target_port = 1.337,
                protocol = 'tcp',
                application_id = '0'
            )
        else:
            return PortCreateRequest(
                published_port = 1.337,
                target_port = 1.337,
                application_id = '0',
        )
        """

    def testPortCreateRequest(self):
        """Test PortCreateRequest"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)


if __name__ == "__main__":
    unittest.main()
