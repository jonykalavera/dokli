"""Manifest model tests."""

import pytest
import yaml

from dokli.manifest import ApplicationService, ComposeService, DatabaseService, Manifest, Resource


def _load_manifest(raw_yaml: str) -> Manifest:
    return Manifest.model_validate(yaml.safe_load(raw_yaml))


class TestResource:
    """Generic resource model tests (issue #50)."""

    def test_in_alias(self):
        """We expect the in field to be populated from the YAML `in` key."""
        resource = Resource.model_validate({"kind": "domain", "name": "x.example.com", "in": "compose:web", "data": {"host": "x.example.com"}})
        assert resource.in_ == "compose:web"

    def test_manifest_resources_and_version(self):
        """We expect the manifest to carry resources, apiVersion and dokployVersion."""
        manifest = _load_manifest(
            """
            apiVersion: v1
            dokployVersion: "0.29.13"
            connection: prod
            resources:
              - kind: domain
                name: x.example.com
                in: compose:web
                data: { host: x.example.com }
            """
        )
        assert manifest.api_version == "v1"
        assert manifest.dokploy_version == "0.29.13"
        assert len(manifest.resources) == 1
        assert manifest.resources[0].kind == "domain"

    def test_load_rejects_unknown_api_version(self, tmp_path):
        """We expect an unsupported apiVersion to fail on load."""
        target = tmp_path / "dokploy.yaml"
        target.write_text("apiVersion: v2\nconnection: prod\n")
        with pytest.raises(ValueError):
            Manifest.load(str(target))


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

    def test_database_service(self):
        """We expect database services to be parsed."""
        manifest = _load_manifest(
            """
            connection: prod
            projects:
              - name: myapp
                services:
                  - type: postgres
                    name: db
                    database_name: appdb
                    database_user: app
                    password_cmd: "secret-tool lookup dokli db"
            """
        )
        service = manifest.projects[0].services[0]
        assert isinstance(service, DatabaseService)
        assert service.database_name == "appdb"
        assert service.password_cmd == "secret-tool lookup dokli db"

    def test_environments(self):
        """We expect named environments to be parsed."""
        manifest = _load_manifest(
            """
            connection: prod
            projects:
              - name: myapp
                services:
                  - type: compose
                    name: backend
                environments:
                  - name: staging
                    services:
                      - type: compose
                        name: api
            """
        )
        project = manifest.projects[0]
        assert project.services[0].name == "backend"
        assert project.environments[0].name == "staging"
        assert project.environments[0].services[0].name == "api"

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
