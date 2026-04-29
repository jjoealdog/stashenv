"""CLI commands for managing profile aliases."""

from __future__ import annotations

import click

from stashenv.store import _store_dir
from stashenv.alias import (
    set_alias,
    remove_alias,
    resolve_alias,
    list_aliases,
    AliasNotFoundError,
    AliasAlreadyExistsError,
)


@click.group("alias")
def alias_group():
    """Manage short aliases for profiles."""


@alias_group.command("set")
@click.argument("alias")
@click.argument("profile")
@click.option("--overwrite", "-f", is_flag=True, default=False, help="Overwrite existing alias")
def set_cmd(alias: str, profile: str, overwrite: bool):
    """Map ALIAS to PROFILE."""
    store = _store_dir()
    try:
        set_alias(store, alias, profile, overwrite=overwrite)
        click.echo(f"Alias '{alias}' -> '{profile}' saved.")
    except AliasAlreadyExistsError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
    except ValueError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@alias_group.command("remove")
@click.argument("alias")
def remove_cmd(alias: str):
    """Remove an alias."""
    store = _store_dir()
    try:
        remove_alias(store, alias)
        click.echo(f"Alias '{alias}' removed.")
    except AliasNotFoundError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@alias_group.command("resolve")
@click.argument("alias")
def resolve_cmd(alias: str):
    """Print the profile name that ALIAS points to."""
    store = _store_dir()
    try:
        profile = resolve_alias(store, alias)
        click.echo(profile)
    except AliasNotFoundError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@alias_group.command("list")
def list_cmd():
    """List all aliases."""
    store = _store_dir()
    aliases = list_aliases(store)
    if not aliases:
        click.echo("No aliases defined.")
        return
    for alias, profile in sorted(aliases.items()):
        click.echo(f"{alias}  ->  {profile}")


def register(cli: click.Group) -> None:
    cli.add_command(alias_group)
