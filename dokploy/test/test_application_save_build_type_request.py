
"""Dokploy API

Endpoints for dokploy

The version of the OpenAPI document: v0.6.1
Generated by OpenAPI Generator (https://openapi-generator.tech)

Do not edit the class manually.
"""  # noqa: E501

import unittest

from openapi_client.models.application_save_build_type_request import ApplicationSaveBuildTypeRequest


class TestApplicationSaveBuildTypeRequest(unittest.TestCase):
    """ApplicationSaveBuildTypeRequest unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> ApplicationSaveBuildTypeRequest:
        """Test ApplicationSaveBuildTypeRequest
        include_optional is a boolean, when False only required
        params are included, when True both required and
        optional params are included
        """
        # uncomment below to create an instance of `ApplicationSaveBuildTypeRequest`
        """
        model = ApplicationSaveBuildTypeRequest()
        if include_optional:
            return ApplicationSaveBuildTypeRequest(
                application_id = '',
                build_type = 'dockerfile',
                dockerfile = '',
                docker_context_path = '',
                publish_directory = ''
            )
        else:
            return ApplicationSaveBuildTypeRequest(
                application_id = '',
                build_type = 'dockerfile',
                docker_context_path = '',
        )
        """

    def testApplicationSaveBuildTypeRequest(self):
        """Test ApplicationSaveBuildTypeRequest"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)


if __name__ == "__main__":
    unittest.main()
