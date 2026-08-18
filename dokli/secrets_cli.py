"""CLI commands to manage secrets in the system keychain (issue #48)."""

import sys

import typer
from rich import print as rprint
from rich.table import Table

from dokli.secrets import SERVICE, delete_secret, get_secret, set_secret


def build_command() -> typer.Typer:
    """Build the ``dokli secrets`` command group."""
    group = typer.Typer(name="secrets", help="Manage secrets in the system keychain.", no_args_is_help=True)

    @group.command("set")
    def set_secret_cmd(
        account: str = typer.Argument(..., help="Account name, e.g. conn.<name>."),
        stdin: bool = typer.Option(False, "--stdin", help="Read the value from stdin instead of prompting."),
    ) -> None:
        """Store a secret (value is prompted hidden, or read from stdin)."""
        value = _read_secret(stdin)
        if not value:
            raise typer.BadParameter("Empty value.")
        set_secret(account, value)
        rprint(f"[green]Stored secret '{account}'.[/green]")

    @group.command("get")
    def get_secret_cmd(
        account: str = typer.Argument(..., help="Account name, e.g. conn.<name>."),
        show: bool = typer.Option(False, "--show", help="Print the value in plain text."),
    ) -> None:
        """Show a stored secret (masked by default)."""
        value = get_secret(account)
        if value is None:
            rprint(f"[red]No secret stored for '{account}'.[/red]")
            raise typer.Exit(code=1)
        rprint(value if show else _mask(value))

    @group.command("rm")
    def remove_secret_cmd(account: str = typer.Argument(..., help="Account name, e.g. conn.<name>.")) -> None:
        """Remove a stored secret."""
        delete_secret(account)
        rprint(f"[green]Removed secret '{account}'.[/green]")

    @group.command("ls")
    def list_secrets_cmd() -> None:
        """List stored secrets (best effort; not all keyring backends support it)."""
        import keyring

        backend = keyring.get_keyring()
        list_method = getattr(backend, "list", None)
        if list_method is None:
            rprint("[yellow]Listing is not supported by this keyring backend.[/yellow]")
            return
        table = Table(title="Secrets")
        table.add_column("Account")
        for service, account in list_method():
            if service == SERVICE:
                table.add_row(account)
        rprint(table)

    return group


def _read_secret(stdin: bool) -> str:
    """Read a secret value from stdin or a hidden prompt."""
    if stdin:
        return sys.stdin.readline().strip("\n")
    return typer.prompt("Value", hide_input=True)


def _mask(value: str) -> str:
    """Mask a secret value, showing only the first and last four characters."""
    if len(value) <= 8:
        return "***"
    return f"{value[:4]}…{value[-4:]}"
