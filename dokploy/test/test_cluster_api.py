
"""Dokploy API

Endpoints for dokploy

The version of the OpenAPI document: v0.6.1
Generated by OpenAPI Generator (https://openapi-generator.tech)

Do not edit the class manually.
"""  # noqa: E501

import unittest

from openapi_client.api.cluster_api import ClusterApi


class TestClusterApi(unittest.TestCase):
    """ClusterApi unit test stubs"""

    def setUp(self) -> None:
        self.api = ClusterApi()

    def tearDown(self) -> None:
        pass

    def test_cluster_add_manager(self) -> None:
        """Test case for cluster_add_manager"""
        pass

    def test_cluster_add_worker(self) -> None:
        """Test case for cluster_add_worker"""
        pass

    def test_cluster_get_nodes(self) -> None:
        """Test case for cluster_get_nodes"""
        pass

    def test_cluster_remove_worker(self) -> None:
        """Test case for cluster_remove_worker"""
        pass


if __name__ == "__main__":
    unittest.main()