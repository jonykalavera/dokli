
"""Dokploy API

Endpoints for dokploy

The version of the OpenAPI document: v0.6.1
Generated by OpenAPI Generator (https://openapi-generator.tech)

Do not edit the class manually.
"""  # noqa: E501

import unittest

from openapi_client.models.docker_get_containers_by_app_name_match_app_type_parameter import (
    DockerGetContainersByAppNameMatchAppTypeParameter,
)


class TestDockerGetContainersByAppNameMatchAppTypeParameter(unittest.TestCase):
    """DockerGetContainersByAppNameMatchAppTypeParameter unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> DockerGetContainersByAppNameMatchAppTypeParameter:
        """Test DockerGetContainersByAppNameMatchAppTypeParameter
        include_optional is a boolean, when False only required
        params are included, when True both required and
        optional params are included
        """
        # uncomment below to create an instance of `DockerGetContainersByAppNameMatchAppTypeParameter`
        """
        model = DockerGetContainersByAppNameMatchAppTypeParameter()
        if include_optional:
            return DockerGetContainersByAppNameMatchAppTypeParameter(
            )
        else:
            return DockerGetContainersByAppNameMatchAppTypeParameter(
        )
        """

    def testDockerGetContainersByAppNameMatchAppTypeParameter(self):
        """Test DockerGetContainersByAppNameMatchAppTypeParameter"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)


if __name__ == "__main__":
    unittest.main()
