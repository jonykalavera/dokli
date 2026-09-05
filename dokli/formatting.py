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

#: Secret-like key words, matched case-insensitively against each word of a
#: field name. Words are produced by splitting the key on camelCase boundaries
#: and non-alphanumeric separators, so short fragments (``pass``, ``key``,
#: ``pat``) only fire when they stand alone: ``REDIS_PASS`` and ``GH_PAT`` are
#: masked, while ``PATH``, ``BYPASS`` or ``hockey`` are not.
SECRET_KEY_WORDS: frozenset[str] = frozenset(
    {
        "pass",
        "password",
        "passwd",
        "pwd",
        "secret",
        "token",
        "key",
        "pat",
        "credential",
        "credentials",
        "cred",
        "auth",
        "authentication",
        "dsn",
        "private",
    }
)

#: Field names whose string value is a multi-line ``KEY=VALUE`` env blob. Every
#: value is masked by default; ``reveal_env`` keeps the listed keys in plain text.
ENV_BLOB_FIELDS: frozenset[str] = frozenset({"env", "previewEnv", "envVariables"})

#: Field names whose value is an opaque secret blob (mount content, backup
#: metadata, build args). The whole value is masked by default.
SECRET_BLOB_FIELDS: frozenset[str] = frozenset({"content", "metadata", "buildArgs", "previewBuildArgs"})

_CAMEL_SPLIT = re.compile(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])")
_WORD_SPLIT = re.compile(r"[^A-Za-z0-9]+")

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
    fields: list[str] | None = None,
    reveal_env: frozenset[str] | None = None,
    masked: list[int] | None = None,
) -> str | Table | dict | list:
    """Format the given Response in the given format.

    ``reveal_env`` lists env keys whose values are kept in plain text. When
    ``masked`` is provided, its first element is set to the number of values
    redacted, so callers can surface a ``--show-secrets``/``--show-env`` hint.
    """
    raw_data = response.text
    if not raw_data:
        return ""
    data = json.loads(raw_data)
    if not show_secrets:
        data, count = redact_secrets_counted(data, reveal_env=reveal_env or frozenset())
        if masked is not None:
            masked[0] = count
    data = select_fields(data, fields or [])
    return format_data(data, format, indent=indent)


def _key_words(key: str) -> list[str]:
    """Split a field name into lowercase words on separators and camelCase."""
    words: list[str] = []
    for chunk in _WORD_SPLIT.split(key):
        for word in _CAMEL_SPLIT.split(chunk):
            if word:
                words.append(word.lower())
    return words


def _is_secret_key(key: str) -> bool:
    """Whether any word of ``key`` names a secret (``databasePassword``, ``GH_PAT``)."""
    return any(word in SECRET_KEY_WORDS for word in _key_words(key))


class _Redactor:
    """Recursive secret redactor that counts the values it masks.

    Secret-named fields are redacted wherever they appear. Env-like blobs
    (``env``, ``previewEnv``, ``envVariables``) are multi-line ``KEY=VALUE``
    strings whose values are all masked by default; ``reveal_env`` lists the
    keys whose values are kept in plain text. Opaque secret blobs (``content``,
    ``metadata``, ``buildArgs``, ...) are masked whole.
    """

    def __init__(self, reveal_env: frozenset[str] = frozenset()) -> None:
        self.masked = 0
        self.reveal_env = reveal_env

    def redact(self, data: Any) -> Any:
        match data:
            case dict():
                redacted = {}
                for key, value in data.items():
                    name = str(key)
                    if _is_secret_key(name):
                        if value is None:
                            redacted[key] = None
                        else:
                            self.masked += 1
                            redacted[key] = "***"
                    elif name in ENV_BLOB_FIELDS and isinstance(value, str):
                        redacted[key] = self._redact_env(value)
                    elif name in SECRET_BLOB_FIELDS and value is not None:
                        self.masked += 1
                        redacted[key] = "***"
                    else:
                        redacted[key] = self.redact(value)
                return redacted
            case list():
                return [self.redact(item) for item in data]
            case _:
                return data

    def _redact_env(self, value: str) -> str:
        lines = []
        previous_masked = False
        for line in value.splitlines():
            if "=" in line:
                key, _, _ = line.partition("=")
                if key in self.reveal_env:
                    previous_masked = False
                    lines.append(line)
                else:
                    self.masked += 1
                    previous_masked = True
                    lines.append(f"{key}=***")
            elif previous_masked:
                # Continuation of a masked multi-line value (e.g. a PEM block).
                lines.append("***")
            else:
                lines.append(line)
        return "\n".join(lines)


def redact_secrets(data: Any) -> Any:
    """Recursively replace secret values with ``***``.

    Secret-named fields (``password``, ``secret``, ``token``, ``key``, ...) are
    redacted wherever they appear. Env-like blobs and opaque secret blobs are
    masked by default too; use :func:`redact_secrets_counted` with
    ``reveal_env`` to keep specific env keys in plain text.
    """
    return _Redactor().redact(data)


def redact_secrets_counted(data: Any, reveal_env: frozenset[str] = frozenset()) -> tuple[Any, int]:
    """Redact secrets and return the masked-value count alongside.

    ``reveal_env`` lists env keys whose values are kept in plain text.
    """
    redactor = _Redactor(reveal_env)
    return redactor.redact(data), redactor.masked


def select_fields(data: Any, fields: list[str]) -> Any:
    """Keep only the given top-level fields of a dict (or of each dict in a list).

    ``None`` fields filter to ``None``; scalars and lists of scalars pass
    through untouched. Unknown field names are dropped. ``fields=[]`` returns
    the data unchanged.
    """
    if not fields:
        return data
    match data:
        case dict():
            return {key: data[key] for key in fields if key in data}
        case list():
            return [select_fields(item, fields) for item in data]
        case _:
            return data


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
