
"""Dokploy API

Endpoints for dokploy

The version of the OpenAPI document: v0.6.1
Generated by OpenAPI Generator (https://openapi-generator.tech)

Do not edit the class manually.
"""  # noqa: E501

import unittest

from openapi_client.models.auth_verify2_fa_setup_request import AuthVerify2FASetupRequest


class TestAuthVerify2FASetupRequest(unittest.TestCase):
    """AuthVerify2FASetupRequest unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> AuthVerify2FASetupRequest:
        """Test AuthVerify2FASetupRequest
        include_optional is a boolean, when False only required
        params are included, when True both required and
        optional params are included
        """
        # uncomment below to create an instance of `AuthVerify2FASetupRequest`
        """
        model = AuthVerify2FASetupRequest()
        if include_optional:
            return AuthVerify2FASetupRequest(
                pin = '012345',
                secret = '0'
            )
        else:
            return AuthVerify2FASetupRequest(
                pin = '012345',
                secret = '0',
        )
        """

    def testAuthVerify2FASetupRequest(self):
        """Test AuthVerify2FASetupRequest"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)


if __name__ == "__main__":
    unittest.main()
