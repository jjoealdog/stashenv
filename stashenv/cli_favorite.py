"""CLI commands for managing favorite profiles."""

import click
from pathlib import Path
from stashenv.store import _store_dir, list_profiles
from stashenv.favorite import (
    add_favorite,
    remove_favorite,
    list_favorites,
    is_favorite,
    FavoriteNotFoundError,
)


@click.group(name="favorite")
def favorite_group():
    """Manage favorite (starred) profiles."""


@favorite_group.command(name="add")
@click.argument("profile")
def add_cmd(profile: str):
    """Mark a profile as a favorite."""
    store = _store_dir()
    known = list_profiles(store)
    if profile not in known:
        click.echo(f"Error: profile '{profile}' does not exist.", err=True)
        raise SystemExit(1)
    add_favorite(store, profile)
    star = "⭐" if not click.utils.should_strip_ansi() else "*"
    click.echo(f"{star} '{profile}' added to favorites.")


@favorite_group.command(name="remove")
@click.argument("profile")
def remove_cmd(profile: str):
    """Remove a profile from favorites."""
    store = _store_dir()
    try:
        remove_favorite(store, profile)
        click.echo(f"'{profile}' removed from favorites.")
    except FavoriteNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@favorite_group.command(name="list")
def list_cmd():
    """List all favorited profiles."""
    store = _store_dir()
    favs = list_favorites(store)
    if not favs:
        click.echo("No favorites set.")
        return
    for name in favs:
        click.echo(f"  * {name}")


@favorite_group.command(name="check")
@click.argument("profile")
def check_cmd(profile: str):
    """Check whether a profile is marked as a favorite."""
    store = _store_dir()
    if is_favorite(store, profile):
        click.echo(f"'{profile}' is a favorite.")
    else:
        click.echo(f"'{profile}' is not a favorite.")


def register(cli: click.Group):
    cli.add_command(favorite_group)
