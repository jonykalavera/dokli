
"""Dokploy API

Endpoints for dokploy

The version of the OpenAPI document: v0.6.1
Generated by OpenAPI Generator (https://openapi-generator.tech)

Do not edit the class manually.
"""  # noqa: E501

import unittest

from openapi_client.models.registry_create_request import RegistryCreateRequest


class TestRegistryCreateRequest(unittest.TestCase):
    """RegistryCreateRequest unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> RegistryCreateRequest:
        """Test RegistryCreateRequest
        include_optional is a boolean, when False only required
        params are included, when True both required and
        optional params are included
        """
        # uncomment below to create an instance of `RegistryCreateRequest`
        """
        model = RegistryCreateRequest()
        if include_optional:
            return RegistryCreateRequest(
                registry_name = '0',
                username = '0',
                password = '0',
                registry_url = '',
                registry_type = 'selfHosted',
                image_prefix = ''
            )
        else:
            return RegistryCreateRequest(
                registry_name = '0',
                username = '0',
                password = '0',
                registry_url = '',
                registry_type = 'selfHosted',
                image_prefix = '',
        )
        """

    def testRegistryCreateRequest(self):
        """Test RegistryCreateRequest"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)


if __name__ == "__main__":
    unittest.main()
