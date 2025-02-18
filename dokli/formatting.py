"""Dokli formatting utility functions."""

import json
from enum import Enum
from typing import TypeVar

import typer
import yaml
from httpx import Response
from rich.table import Table

app = typer.Typer()


class Format(str, Enum):
    """API response format."""

    python = "python"
    json = "json"
    yaml = "yaml"
    table = "table"


def format_response(response: Response, format: Format) -> str | Table | dict | list:
    """Format the given Response in the given format."""
    raw_data = response.text
    if not raw_data:
        return ""
    data = json.loads(raw_data)
    return format_data(data, format)


D = TypeVar("D")


def format_data(data: D, format: Format) -> str | D | Table:
    """Format the given data in the given format."""
    match format:
        case Format.python:
            return data
        case Format.json:
            return json.dumps(data)
        case Format.yaml:
            return yaml.dump(data)
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
