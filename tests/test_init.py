"""Init tests."""

import pytest

from dokli.config import Config
from dokli.init import init_manifest


class TestInitManifest:
    """Manifest scaffolding tests."""

    def test_writes_template(self, tmp_path):
        """We expect a manifest template to be written."""
        config = Config(connections=[])
        output = str(tmp_path / "dokploy.yaml")

        path = init_manifest(config, output)

        content = open(path).read()
        assert "connection: <connection-name>" in content
        assert "projects: []" in content

    def test_uses_first_connection(self, tmp_path):
        """We expect the first connection name to be used."""
        config = Config.model_validate(
            {"connections": [{"name": "prod", "url": "https://example.com", "api_key_cmd": "echo key"}]}
        )
        output = str(tmp_path / "dokploy.yaml")

        init_manifest(config, output)

        assert "connection: prod" in open(output).read()

    def test_refuses_to_overwrite(self, tmp_path):
        """We expect an error when the output file already exists."""
        config = Config(connections=[])
        output = str(tmp_path / "dokploy.yaml")
        open(output, "w").write("existing")

        with pytest.raises(FileExistsError):
            init_manifest(config, output)
