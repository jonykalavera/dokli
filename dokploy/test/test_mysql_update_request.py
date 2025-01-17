
"""Dokploy API

Endpoints for dokploy

The version of the OpenAPI document: v0.6.1
Generated by OpenAPI Generator (https://openapi-generator.tech)

Do not edit the class manually.
"""  # noqa: E501

import unittest

from openapi_client.models.mysql_update_request import MysqlUpdateRequest


class TestMysqlUpdateRequest(unittest.TestCase):
    """MysqlUpdateRequest unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> MysqlUpdateRequest:
        """Test MysqlUpdateRequest
        include_optional is a boolean, when False only required
        params are included, when True both required and
        optional params are included
        """
        # uncomment below to create an instance of `MysqlUpdateRequest`
        """
        model = MysqlUpdateRequest()
        if include_optional:
            return MysqlUpdateRequest(
                mysql_id = '0',
                name = '0',
                app_name = '0',
                description = '',
                database_name = '0',
                database_user = '0',
                database_password = '',
                database_root_password = '',
                docker_image = 'mysql:8',
                command = '',
                env = '',
                memory_reservation = 1.337,
                memory_limit = 1.337,
                cpu_reservation = 1.337,
                cpu_limit = 1.337,
                external_port = 1.337,
                application_status = 'idle',
                created_at = '',
                project_id = ''
            )
        else:
            return MysqlUpdateRequest(
                mysql_id = '0',
        )
        """

    def testMysqlUpdateRequest(self):
        """Test MysqlUpdateRequest"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)


if __name__ == "__main__":
    unittest.main()
