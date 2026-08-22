"""The ``dokli ls`` command: a flat list of services and their ids."""

from collections.abc import Callable

import typer
from rich import print as rprint
from rich.table import Table

from dokli.api_client import APIClient
from dokli.config import Config, complete_connection_names, resolve_connection
from dokli.state import collect_state


def build_command(config: Config) -> Callable[..., None]:
    """Return the ``ls`` command function, bound to ``config``."""

    def ls_command(
        connection_name: str | None = typer.Argument(
            None, help="Connection name.", shell_complete=complete_connection_names
        ),
        service_type: str | None = typer.Option(
            None,
            "--type",
            "-t",
            help="Only list services of this type (compose|application|postgres|mysql|mariadb|mongo|redis).",
        ),
        search: str | None = typer.Option(
            None, "--search", "-s", help="Only list services whose name matches this substring."
        ),
    ) -> None:
        """List services and their ids across the instance."""
        connection = resolve_connection(config, connection_name)
        client = APIClient(connection)
        state = collect_state(connection, client=client)

        rows: list[dict[str, str]] = []
        for project in state.projects:
            for environment in project.environments:
                for service in environment.services:
                    if service_type is not None and service.type != service_type:
                        continue
                    if search is not None and search.lower() not in service.name.lower():
                        continue
                    rows.append(
                        {
                            "project": project.name,
                            "environment": environment.name,
                            "type": service.type,
                            "name": service.name,
                            "app_name": service.app_name,
                            "id": service.service_id,
                        }
                    )

        _render(rows)

    return ls_command


def _render(rows: list[dict[str, str]]) -> None:
    """Print the rows as a table (or a notice when empty)."""
    if not rows:
        rprint("[yellow]No services found.[/yellow]")
        return
    columns = ("project", "environment", "type", "name", "app_name", "id")
    table = Table(title="Services")
    for column in columns:
        table.add_column(column, style="bold" if column in ("name", "id") else None)
    for row in rows:
        table.add_row(*(str(row[column]) for column in columns))
    rprint(table)
