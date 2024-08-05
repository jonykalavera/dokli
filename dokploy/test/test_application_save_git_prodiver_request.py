
"""Dokploy API

Endpoints for dokploy

The version of the OpenAPI document: v0.6.1
Generated by OpenAPI Generator (https://openapi-generator.tech)

Do not edit the class manually.
"""  # noqa: E501

import unittest

from openapi_client.models.application_save_git_prodiver_request import ApplicationSaveGitProdiverRequest


class TestApplicationSaveGitProdiverRequest(unittest.TestCase):
    """ApplicationSaveGitProdiverRequest unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> ApplicationSaveGitProdiverRequest:
        """Test ApplicationSaveGitProdiverRequest
        include_optional is a boolean, when False only required
        params are included, when True both required and
        optional params are included
        """
        # uncomment below to create an instance of `ApplicationSaveGitProdiverRequest`
        """
        model = ApplicationSaveGitProdiverRequest()
        if include_optional:
            return ApplicationSaveGitProdiverRequest(
                custom_git_branch = '',
                application_id = '',
                custom_git_build_path = '',
                custom_git_url = '',
                custom_git_ssh_key_id = ''
            )
        else:
            return ApplicationSaveGitProdiverRequest(
                application_id = '',
        )
        """

    def testApplicationSaveGitProdiverRequest(self):
        """Test ApplicationSaveGitProdiverRequest"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)


if __name__ == "__main__":
    unittest.main()
