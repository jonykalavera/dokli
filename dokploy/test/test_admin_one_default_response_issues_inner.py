
"""Dokploy API

Endpoints for dokploy

The version of the OpenAPI document: v0.6.1
Generated by OpenAPI Generator (https://openapi-generator.tech)

Do not edit the class manually.
"""  # noqa: E501

import unittest

from openapi_client.models.admin_one_default_response_issues_inner import AdminOneDefaultResponseIssuesInner


class TestAdminOneDefaultResponseIssuesInner(unittest.TestCase):
    """AdminOneDefaultResponseIssuesInner unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> AdminOneDefaultResponseIssuesInner:
        """Test AdminOneDefaultResponseIssuesInner
        include_optional is a boolean, when False only required
        params are included, when True both required and
        optional params are included
        """
        # uncomment below to create an instance of `AdminOneDefaultResponseIssuesInner`
        """
        model = AdminOneDefaultResponseIssuesInner()
        if include_optional:
            return AdminOneDefaultResponseIssuesInner(
                message = ''
            )
        else:
            return AdminOneDefaultResponseIssuesInner(
                message = '',
        )
        """

    def testAdminOneDefaultResponseIssuesInner(self):
        """Test AdminOneDefaultResponseIssuesInner"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)


if __name__ == "__main__":
    unittest.main()