
"""Dokploy API

Endpoints for dokploy

The version of the OpenAPI document: v0.6.1
Generated by OpenAPI Generator (https://openapi-generator.tech)

Do not edit the class manually.
"""  # noqa: E501

import unittest

from openapi_client.api.compose_api import ComposeApi


class TestComposeApi(unittest.TestCase):
    """ComposeApi unit test stubs"""

    def setUp(self) -> None:
        self.api = ComposeApi()

    def tearDown(self) -> None:
        pass

    def test_compose_all_services(self) -> None:
        """Test case for compose_all_services"""
        pass

    def test_compose_clean_queues(self) -> None:
        """Test case for compose_clean_queues"""
        pass

    def test_compose_create(self) -> None:
        """Test case for compose_create"""
        pass

    def test_compose_delete(self) -> None:
        """Test case for compose_delete"""
        pass

    def test_compose_deploy(self) -> None:
        """Test case for compose_deploy"""
        pass

    def test_compose_deploy_template(self) -> None:
        """Test case for compose_deploy_template"""
        pass

    def test_compose_get_default_command(self) -> None:
        """Test case for compose_get_default_command"""
        pass

    def test_compose_get_tags(self) -> None:
        """Test case for compose_get_tags"""
        pass

    def test_compose_one(self) -> None:
        """Test case for compose_one"""
        pass

    def test_compose_randomize_compose(self) -> None:
        """Test case for compose_randomize_compose"""
        pass

    def test_compose_redeploy(self) -> None:
        """Test case for compose_redeploy"""
        pass

    def test_compose_refresh_token(self) -> None:
        """Test case for compose_refresh_token"""
        pass

    def test_compose_stop(self) -> None:
        """Test case for compose_stop"""
        pass

    def test_compose_templates(self) -> None:
        """Test case for compose_templates"""
        pass

    def test_compose_update(self) -> None:
        """Test case for compose_update"""
        pass


if __name__ == "__main__":
    unittest.main()
