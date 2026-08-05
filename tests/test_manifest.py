"""Manifest model tests."""

import pytest
import yaml

from dokli.manifest import ApplicationService, ComposeService, Manifest


def _load_manifest(raw_yaml: str) -> Manifest:
    return Manifest.model_validate(yaml.safe_load(raw_yaml))


class TestManifest:
    """Manifest model tests."""

    def test_parse_manifest(self):
        """We expect to be able to parse a manifest from YAML."""
        manifest = _load_manifest(
            """
            connection: prod
            git_providers:
              - name: github-main
                provider: github
            projects:
              - name: myapp
                services:
                  - type: compose
                    name: backend
            """
        )
        assert manifest.connection == "prod"
        assert manifest.git_providers[0].name == "github-main"
        assert manifest.projects[0].name == "myapp"

    def test_service_discriminated_union(self):
        """We expect services to be discriminated by type."""
        manifest = _load_manifest(
            """
            connection: prod
            projects:
              - name: myapp
                services:
                  - type: compose
                    name: backend
                  - type: application
                    name: web
            """
        )
        service = manifest.projects[0].services
        assert isinstance(service[0], ComposeService)
        assert isinstance(service[1], ApplicationService)

    def test_get_git_provider_raises_for_unknown(self):
        """We expect an error when a git provider is not defined."""
        manifest = _load_manifest(
            """
            connection: prod
            projects: []
            """
        )
        with pytest.raises(ValueError, match="not defined"):
            manifest.get_git_provider("missing")

    def test_get_git_provider_by_name(self):
        """We expect to look up git providers by name."""
        manifest = _load_manifest(
            """
            connection: prod
            git_providers:
              - name: github-main
                provider: github
            """
        )
        assert manifest.get_git_provider("github-main").provider == "github"
