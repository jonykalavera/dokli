"""Stable error channel tests: consistent exit codes and machine-readable errors."""

import json

import pytest
import typer

from dokli.errors import EXIT_ERROR, EXIT_OK, EXIT_USAGE, emit_error, format_from_argv
from dokli.formatting import Format


class TestExitCodes:
    """Documented exit code constants."""

    def test_ok_is_zero(self):
        """We expect success to be exit 0."""
        assert EXIT_OK == 0

    def test_runtime_error_is_one(self):
        """We expect runtime/API errors to be exit 1."""
        assert EXIT_ERROR == 1

    def test_usage_error_is_two(self):
        """We expect usage errors to be exit 2."""
        assert EXIT_USAGE == 2


class TestEmitError:
    """The emit_error helper."""

    def test_json_format_writes_json_to_stderr(self, capsys):
        """We expect a JSON error object on stderr under --format json."""
        with pytest.raises(typer.Exit) as excinfo:
            emit_error("boom", format=Format.json)
        assert excinfo.value.exit_code == EXIT_ERROR
        data = json.loads(capsys.readouterr().err)
        assert data == {"error": "boom", "exit_code": 1}

    def test_agent_format_writes_json_to_stderr(self, capsys):
        """We expect a JSON error object on stderr under --format agent."""
        with pytest.raises(typer.Exit) as excinfo:
            emit_error("boom", format=Format.agent)
        assert excinfo.value.exit_code == EXIT_ERROR
        data = json.loads(capsys.readouterr().err)
        assert data == {"error": "boom", "exit_code": 1}

    def test_human_format_writes_rich_red(self, capsys):
        """We expect rich red text on stderr for non-machine formats."""
        with pytest.raises(typer.Exit):
            emit_error("boom", format=Format.yaml)
        err = capsys.readouterr().err
        assert "boom" in err
        assert not err.startswith("{")

    def test_custom_exit_code(self, capsys):
        """We expect a custom exit code to be honored."""
        with pytest.raises(typer.Exit) as excinfo:
            emit_error("boom", format=Format.json, exit_code=EXIT_USAGE)
        assert excinfo.value.exit_code == EXIT_USAGE
        assert json.loads(capsys.readouterr().err)["exit_code"] == 2

    def test_default_format_is_human(self, capsys):
        """We expect emit_error to default to rich red when no format is given."""
        with pytest.raises(typer.Exit):
            emit_error("boom")
        assert "boom" in capsys.readouterr().err


class TestFormatFromArgv:
    """Detecting --format from raw argv (top-level entry)."""

    def test_detects_dash_dash_format(self):
        """We expect `--format json` to be detected."""
        assert format_from_argv(["ls", "--format", "json"]) == Format.json

    def test_detects_equals_format(self):
        """We expect `--format=agent` to be detected."""
        assert format_from_argv(["ls", "--format=agent"]) == Format.agent

    def test_detects_only_machine_formats(self):
        """We expect yaml to return None (not machine-readable)."""
        assert format_from_argv(["ls", "--format", "yaml"]) is None

    def test_none_when_absent(self):
        """We expect None when no --format is present."""
        assert format_from_argv(["ls", "meche"]) is None

    def test_defaults_to_sys_argv(self, monkeypatch):
        """We expect argv to default to sys.argv."""
        monkeypatch.setattr("sys.argv", ["dokli", "ls", "--format", "agent"])
        assert format_from_argv() == Format.agent
