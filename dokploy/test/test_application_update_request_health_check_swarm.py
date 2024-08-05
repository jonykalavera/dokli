
"""Dokploy API

Endpoints for dokploy

The version of the OpenAPI document: v0.6.1
Generated by OpenAPI Generator (https://openapi-generator.tech)

Do not edit the class manually.
"""  # noqa: E501

import unittest

from openapi_client.models.application_update_request_health_check_swarm import (
    ApplicationUpdateRequestHealthCheckSwarm,
)


class TestApplicationUpdateRequestHealthCheckSwarm(unittest.TestCase):
    """ApplicationUpdateRequestHealthCheckSwarm unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> ApplicationUpdateRequestHealthCheckSwarm:
        """Test ApplicationUpdateRequestHealthCheckSwarm
        include_optional is a boolean, when False only required
        params are included, when True both required and
        optional params are included
        """
        # uncomment below to create an instance of `ApplicationUpdateRequestHealthCheckSwarm`
        """
        model = ApplicationUpdateRequestHealthCheckSwarm()
        if include_optional:
            return ApplicationUpdateRequestHealthCheckSwarm(
                test = [
                    ''
                    ],
                interval = 1.337,
                timeout = 1.337,
                start_period = 1.337,
                retries = 1.337
            )
        else:
            return ApplicationUpdateRequestHealthCheckSwarm(
        )
        """

    def testApplicationUpdateRequestHealthCheckSwarm(self):
        """Test ApplicationUpdateRequestHealthCheckSwarm"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)


if __name__ == "__main__":
    unittest.main()
