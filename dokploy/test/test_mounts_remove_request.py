
"""Dokploy API

Endpoints for dokploy

The version of the OpenAPI document: v0.6.1
Generated by OpenAPI Generator (https://openapi-generator.tech)

Do not edit the class manually.
"""  # noqa: E501

import unittest

from openapi_client.models.mounts_remove_request import MountsRemoveRequest


class TestMountsRemoveRequest(unittest.TestCase):
    """MountsRemoveRequest unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> MountsRemoveRequest:
        """Test MountsRemoveRequest
        include_optional is a boolean, when False only required
        params are included, when True both required and
        optional params are included
        """
        # uncomment below to create an instance of `MountsRemoveRequest`
        """
        model = MountsRemoveRequest()
        if include_optional:
            return MountsRemoveRequest(
                mount_id = ''
            )
        else:
            return MountsRemoveRequest(
                mount_id = '',
        )
        """

    def testMountsRemoveRequest(self):
        """Test MountsRemoveRequest"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)


if __name__ == "__main__":
    unittest.main()