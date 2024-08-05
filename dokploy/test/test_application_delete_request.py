
"""Dokploy API

Endpoints for dokploy

The version of the OpenAPI document: v0.6.1
Generated by OpenAPI Generator (https://openapi-generator.tech)

Do not edit the class manually.
"""  # noqa: E501

import unittest

from openapi_client.models.application_delete_request import ApplicationDeleteRequest


class TestApplicationDeleteRequest(unittest.TestCase):
    """ApplicationDeleteRequest unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> ApplicationDeleteRequest:
        """Test ApplicationDeleteRequest
        include_optional is a boolean, when False only required
        params are included, when True both required and
        optional params are included
        """
        # uncomment below to create an instance of `ApplicationDeleteRequest`
        """
        model = ApplicationDeleteRequest()
        if include_optional:
            return ApplicationDeleteRequest(
                application_id = ''
            )
        else:
            return ApplicationDeleteRequest(
                application_id = '',
        )
        """

    def testApplicationDeleteRequest(self):
        """Test ApplicationDeleteRequest"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)


if __name__ == "__main__":
    unittest.main()
