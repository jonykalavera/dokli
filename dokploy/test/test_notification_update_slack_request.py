
"""Dokploy API

Endpoints for dokploy

The version of the OpenAPI document: v0.6.1
Generated by OpenAPI Generator (https://openapi-generator.tech)

Do not edit the class manually.
"""  # noqa: E501

import unittest

from openapi_client.models.notification_update_slack_request import NotificationUpdateSlackRequest


class TestNotificationUpdateSlackRequest(unittest.TestCase):
    """NotificationUpdateSlackRequest unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> NotificationUpdateSlackRequest:
        """Test NotificationUpdateSlackRequest
        include_optional is a boolean, when False only required
        params are included, when True both required and
        optional params are included
        """
        # uncomment below to create an instance of `NotificationUpdateSlackRequest`
        """
        model = NotificationUpdateSlackRequest()
        if include_optional:
            return NotificationUpdateSlackRequest(
                app_build_error = True,
                database_backup = True,
                dokploy_restart = True,
                name = '',
                app_deploy = True,
                docker_cleanup = True,
                webhook_url = '0',
                channel = '',
                notification_id = '0',
                slack_id = ''
            )
        else:
            return NotificationUpdateSlackRequest(
                notification_id = '0',
                slack_id = '',
        )
        """

    def testNotificationUpdateSlackRequest(self):
        """Test NotificationUpdateSlackRequest"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)


if __name__ == "__main__":
    unittest.main()