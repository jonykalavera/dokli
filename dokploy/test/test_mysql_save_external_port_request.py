
"""Dokploy API

Endpoints for dokploy

The version of the OpenAPI document: v0.6.1
Generated by OpenAPI Generator (https://openapi-generator.tech)

Do not edit the class manually.
"""  # noqa: E501

import unittest

from openapi_client.models.mysql_save_external_port_request import MysqlSaveExternalPortRequest


class TestMysqlSaveExternalPortRequest(unittest.TestCase):
    """MysqlSaveExternalPortRequest unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> MysqlSaveExternalPortRequest:
        """Test MysqlSaveExternalPortRequest
        include_optional is a boolean, when False only required
        params are included, when True both required and
        optional params are included
        """
        # uncomment below to create an instance of `MysqlSaveExternalPortRequest`
        """
        model = MysqlSaveExternalPortRequest()
        if include_optional:
            return MysqlSaveExternalPortRequest(
                mysql_id = '',
                external_port = 1.337
            )
        else:
            return MysqlSaveExternalPortRequest(
                mysql_id = '',
                external_port = 1.337,
        )
        """

    def testMysqlSaveExternalPortRequest(self):
        """Test MysqlSaveExternalPortRequest"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)


if __name__ == "__main__":
    unittest.main()