
"""Dokploy API

Endpoints for dokploy

The version of the OpenAPI document: v0.6.1
Generated by OpenAPI Generator (https://openapi-generator.tech)

Do not edit the class manually.
"""  # noqa: E501

import unittest

from openapi_client.models.postgres_save_external_port_request import PostgresSaveExternalPortRequest


class TestPostgresSaveExternalPortRequest(unittest.TestCase):
    """PostgresSaveExternalPortRequest unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> PostgresSaveExternalPortRequest:
        """Test PostgresSaveExternalPortRequest
        include_optional is a boolean, when False only required
        params are included, when True both required and
        optional params are included
        """
        # uncomment below to create an instance of `PostgresSaveExternalPortRequest`
        """
        model = PostgresSaveExternalPortRequest()
        if include_optional:
            return PostgresSaveExternalPortRequest(
                postgres_id = '',
                external_port = 1.337
            )
        else:
            return PostgresSaveExternalPortRequest(
                postgres_id = '',
                external_port = 1.337,
        )
        """

    def testPostgresSaveExternalPortRequest(self):
        """Test PostgresSaveExternalPortRequest"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)


if __name__ == "__main__":
    unittest.main()
