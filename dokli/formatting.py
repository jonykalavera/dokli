"""Dokli formatting utility functions."""

import json
import re
from enum import Enum
from typing import Any, TypeVar

import typer
import yaml
from httpx import Response
from rich.table import Table

app = typer.Typer()

SECRET_KEY_PATTERN = re.compile(r"(?i)(password|secret|token|api[_-]?key|private[_-]?key|access[_-]?key)")

D = TypeVar("D")


class Format(str, Enum):
    """API response format."""

    python = "python"
    json = "json"
    yaml = "yaml"
    table = "table"
    agent = "agent"


def format_response(
    response: Response,
    format: Format,
    show_secrets: bool = False,
    indent: int = 0,
) -> str | Table | dict | list:
    """Format the given Response in the given format."""
    raw_data = response.text
    if not raw_data:
        return ""
    data = json.loads(raw_data)
    if not show_secrets:
        data = redact_secrets(data)
    return format_data(data, format, indent=indent)


def redact_secrets(data: Any) -> Any:
    """Recursively replace values of secret-like keys with ``***``.

    Keys matching ``password``, ``secret``, ``token``, ``api_key``,
    ``private_key`` or ``access_key`` are redacted. The ``env`` field is
    handled specially: only the values of secret-like variables are redacted.
    """
    match data:
        case dict():
            redacted = {}
            for key, value in data.items():
                if SECRET_KEY_PATTERN.search(str(key)):
                    redacted[key] = "***" if value is not None else None
                elif str(key) == "env" and isinstance(value, str):
                    redacted[key] = _redact_env_lines(value)
                else:
                    redacted[key] = redact_secrets(value)
            return redacted
        case list():
            return [redact_secrets(item) for item in data]
        case _:
            return data


def _redact_env_lines(value: str) -> str:
    lines = []
    for line in value.splitlines():
        if "=" in line:
            key, _, _ = line.partition("=")
            if SECRET_KEY_PATTERN.search(key):
                lines.append(f"{key}=***")
                continue
        lines.append(line)
    return "\n".join(lines)


def _flatten_record(record: Any, prefix: str = "") -> dict[str, Any]:
    """Flatten a nested record into flat keys joined with ``__``.

    ``{"network": {"down": 1.0}}`` becomes ``{"network__down": 1.0}``. Lists
    stay as-is (a JSON column value). ``None``/scalars are kept.
    """
    flat: dict[str, Any] = {}
    if isinstance(record, dict):
        for key, value in record.items():
            name = f"{prefix}{key}" if not prefix else f"{prefix}__{key}"
            if isinstance(value, dict):
                flat.update(_flatten_record(value, name))
            else:
                flat[name] = value
    else:
        flat[prefix or "value"] = record
    return flat


def _format_agent(data: D) -> str:
    """Serialize data as a header row + one NDJSON row per record.

    Line 1 is the column names (array of strings); every following line is one
    record's values (array). Nested objects are flattened with ``__``.
    """
    records: list[dict[str, Any]]
    if isinstance(data, list):
        records = [_flatten_record(item) for item in data if isinstance(item, dict)]
    elif isinstance(data, dict):
        records = [_flatten_record(data)]
    else:
        return json.dumps(["value"]) + "\n" + json.dumps([data]) + "\n"

    columns: list[str] = []
    for record in records:
        for key in record:
            if key not in columns:
                columns.append(key)
    lines = [json.dumps(columns)]
    for record in records:
        lines.append(json.dumps([record.get(column) for column in columns]))
    return "\n".join(lines) + "\n"


def format_data(data: D, format: Format, indent: int = 0) -> str | D | Table:
    """Format the given data in the given format."""
    match format:
        case Format.python:
            return data
        case Format.json:
            return json.dumps(data, indent=indent or None)
        case Format.yaml:
            return yaml.dump(data)
        case Format.agent:
            return _format_agent(data)
        case Format.table:
            table = _data_to_table(data)
            return table
    return data


def _data_to_table(data: D) -> Table:
    table = Table(title="API Response")
    match data:
        case list():
            if not data:
                return table
            for column in data[0]:
                table.add_column(column)
            for row in data:
                table.add_row(*(str(v) for v in row.values()))
        case dict():
            table.add_column("Key")
            table.add_column("Value")
            for key, value in data.items():
                table.add_row(key, str(value))
    return table
