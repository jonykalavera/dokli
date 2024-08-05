
"""Dokploy API

Endpoints for dokploy

The version of the OpenAPI document: v0.6.1
Generated by OpenAPI Generator (https://openapi-generator.tech)

Do not edit the class manually.
"""  # noqa: E501

import unittest

from openapi_client.models.settings_update_docker_cleanup_request import SettingsUpdateDockerCleanupRequest


class TestSettingsUpdateDockerCleanupRequest(unittest.TestCase):
    """SettingsUpdateDockerCleanupRequest unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> SettingsUpdateDockerCleanupRequest:
        """Test SettingsUpdateDockerCleanupRequest
        include_optional is a boolean, when False only required
        params are included, when True both required and
        optional params are included
        """
        # uncomment below to create an instance of `SettingsUpdateDockerCleanupRequest`
        """
        model = SettingsUpdateDockerCleanupRequest()
        if include_optional:
            return SettingsUpdateDockerCleanupRequest(
                enable_docker_cleanup = True
            )
        else:
            return SettingsUpdateDockerCleanupRequest(
                enable_docker_cleanup = True,
        )
        """

    def testSettingsUpdateDockerCleanupRequest(self):
        """Test SettingsUpdateDockerCleanupRequest"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)


if __name__ == "__main__":
    unittest.main()