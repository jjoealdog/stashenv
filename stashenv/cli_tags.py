"""CLI commands for managing profile tags."""

import click
from stashenv.tags import add_tag, remove_tag, get_tags, profiles_by_tag


@click.group(name="tag")
def tag_group():
    """Manage tags on profiles."""


@tag_group.command(name="add")
@click.argument("profile")
@click.argument("tag")
def add_cmd(profile: str, tag: str):
    """Add TAG to PROFILE."""
    add_tag(profile, tag)
    click.echo(f"Tagged '{profile}' with '{tag}'.")


@tag_group.command(name="remove")
@click.argument("profile")
@click.argument("tag")
def remove_cmd(profile: str, tag: str):
    """Remove TAG from PROFILE."""
    remove_tag(profile, tag)
    click.echo(f"Removed tag '{tag}' from '{profile}'.")


@tag_group.command(name="list")
@click.argument("profile")
def list_cmd(profile: str):
    """List all tags on PROFILE."""
    tags = get_tags(profile)
    if not tags:
        click.echo(f"No tags on '{profile}'.")
    else:
        for t in tags:
            click.echo(t)


@tag_group.command(name="find")
@click.argument("tag")
def find_cmd(tag: str):
    """Find all profiles with TAG."""
    profiles = profiles_by_tag(tag)
    if not profiles:
        click.echo(f"No profiles tagged with '{tag}'.")
    else:
        for p in profiles:
            click.echo(p)
