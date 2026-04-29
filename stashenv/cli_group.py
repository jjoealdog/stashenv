"""CLI commands for profile grouping."""

from __future__ import annotations

import click
from pathlib import Path

from stashenv.store import _store_dir
from stashenv.group import (
    add_to_group,
    remove_from_group,
    list_groups,
    get_group_members,
    get_profile_groups,
    delete_group,
    GroupNotFoundError,
    ProfileNotInGroupError,
)


@click.group("group")
def group_group() -> None:
    """Manage profile groups."""


@group_group.command("add")
@click.argument("group")
@click.argument("profile")
def add_cmd(group: str, profile: str) -> None:
    """Add PROFILE to GROUP."""
    store = _store_dir()
    add_to_group(store, group, profile)
    click.echo(f"Added '{profile}' to group '{group}'.")


@group_group.command("remove")
@click.argument("group")
@click.argument("profile")
def remove_cmd(group: str, profile: str) -> None:
    """Remove PROFILE from GROUP."""
    store = _store_dir()
    try:
        remove_from_group(store, group, profile)
        click.echo(f"Removed '{profile}' from group '{group}'.")
    except GroupNotFoundError:
        click.echo(f"Error: group '{group}' not found.", err=True)
        raise SystemExit(1)
    except ProfileNotInGroupError:
        click.echo(f"Error: profile '{profile}' is not in group '{group}'.", err=True)
        raise SystemExit(1)


@group_group.command("list")
def list_cmd() -> None:
    """List all groups."""
    store = _store_dir()
    groups = list_groups(store)
    if not groups:
        click.echo("No groups defined.")
        return
    for g in groups:
        click.echo(g)


@group_group.command("members")
@click.argument("group")
def members_cmd(group: str) -> None:
    """List profiles in GROUP."""
    store = _store_dir()
    try:
        members = get_group_members(store, group)
    except GroupNotFoundError:
        click.echo(f"Error: group '{group}' not found.", err=True)
        raise SystemExit(1)
    if not members:
        click.echo(f"Group '{group}' is empty.")
        return
    for m in members:
        click.echo(m)


@group_group.command("of")
@click.argument("profile")
def of_cmd(profile: str) -> None:
    """List groups that PROFILE belongs to."""
    store = _store_dir()
    groups = get_profile_groups(store, profile)
    if not groups:
        click.echo(f"'{profile}' is not in any group.")
        return
    for g in groups:
        click.echo(g)


@group_group.command("delete")
@click.argument("group")
def delete_cmd(group: str) -> None:
    """Delete an entire GROUP."""
    store = _store_dir()
    try:
        delete_group(store, group)
        click.echo(f"Deleted group '{group}'.")
    except GroupNotFoundError:
        click.echo(f"Error: group '{group}' not found.", err=True)
        raise SystemExit(1)


def register(cli: click.Group) -> None:
    cli.add_command(group_group)
