
"""Dokploy API

Endpoints for dokploy

The version of the OpenAPI document: v0.6.1
Generated by OpenAPI Generator (https://openapi-generator.tech)

Do not edit the class manually.
"""  # noqa: E501

import unittest

from openapi_client.models.application_save_github_provider_request import ApplicationSaveGithubProviderRequest


class TestApplicationSaveGithubProviderRequest(unittest.TestCase):
    """ApplicationSaveGithubProviderRequest unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> ApplicationSaveGithubProviderRequest:
        """Test ApplicationSaveGithubProviderRequest
        include_optional is a boolean, when False only required
        params are included, when True both required and
        optional params are included
        """
        # uncomment below to create an instance of `ApplicationSaveGithubProviderRequest`
        """
        model = ApplicationSaveGithubProviderRequest()
        if include_optional:
            return ApplicationSaveGithubProviderRequest(
                application_id = '',
                repository = '',
                branch = '',
                owner = '',
                build_path = ''
            )
        else:
            return ApplicationSaveGithubProviderRequest(
                application_id = '',
                owner = '',
        )
        """

    def testApplicationSaveGithubProviderRequest(self):
        """Test ApplicationSaveGithubProviderRequest"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)


if __name__ == "__main__":
    unittest.main()
