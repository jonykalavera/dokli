
"""Dokploy API

Endpoints for dokploy

The version of the OpenAPI document: v0.6.1
Generated by OpenAPI Generator (https://openapi-generator.tech)

Do not edit the class manually.
"""  # noqa: E501

import unittest

from openapi_client.models.domain_delete_request import DomainDeleteRequest


class TestDomainDeleteRequest(unittest.TestCase):
    """DomainDeleteRequest unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> DomainDeleteRequest:
        """Test DomainDeleteRequest
        include_optional is a boolean, when False only required
        params are included, when True both required and
        optional params are included
        """
        # uncomment below to create an instance of `DomainDeleteRequest`
        """
        model = DomainDeleteRequest()
        if include_optional:
            return DomainDeleteRequest(
                domain_id = ''
            )
        else:
            return DomainDeleteRequest(
                domain_id = '',
        )
        """

    def testDomainDeleteRequest(self):
        """Test DomainDeleteRequest"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)


if __name__ == "__main__":
    unittest.main()
