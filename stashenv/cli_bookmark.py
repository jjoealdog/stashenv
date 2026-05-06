"""CLI commands for managing profile bookmarks."""

from __future__ import annotations

from pathlib import Path

import click

from stashenv.bookmark import (
    add_bookmark,
    remove_bookmark,
    resolve_bookmark,
    list_bookmarks,
    BookmarkNotFoundError,
    BookmarkAlreadyExistsError,
)
from stashenv.store import _store_dir


@click.group("bookmark")
def bookmark_group() -> None:
    """Manage named bookmarks for profiles."""


@bookmark_group.command("add")
@click.argument("name")
@click.argument("profile")
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing bookmark.")
def add_cmd(name: str, profile: str, overwrite: bool) -> None:
    """Create a bookmark NAME pointing to PROFILE."""
    store = _store_dir()
    try:
        add_bookmark(store, name, profile, overwrite=overwrite)
        click.echo(f"Bookmark '{name}' -> '{profile}' saved.")
    except BookmarkAlreadyExistsError:
        click.echo(f"Error: bookmark '{name}' already exists. Use --overwrite to replace.", err=True)
        raise SystemExit(1)
    except ValueError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@bookmark_group.command("remove")
@click.argument("name")
def remove_cmd(name: str) -> None:
    """Delete bookmark NAME."""
    store = _store_dir()
    try:
        remove_bookmark(store, name)
        click.echo(f"Bookmark '{name}' removed.")
    except BookmarkNotFoundError:
        click.echo(f"Error: bookmark '{name}' not found.", err=True)
        raise SystemExit(1)


@bookmark_group.command("resolve")
@click.argument("name")
def resolve_cmd(name: str) -> None:
    """Print the profile that bookmark NAME points to."""
    store = _store_dir()
    try:
        profile = resolve_bookmark(store, name)
        click.echo(profile)
    except BookmarkNotFoundError:
        click.echo(f"Error: bookmark '{name}' not found.", err=True)
        raise SystemExit(1)


@bookmark_group.command("list")
def list_cmd() -> None:
    """List all bookmarks."""
    store = _store_dir()
    bm = list_bookmarks(store)
    if not bm:
        click.echo("No bookmarks defined.")
        return
    for name, profile in sorted(bm.items()):
        click.echo(f"{name:20s}  {profile}")


def register(cli: click.Group) -> None:
    cli.add_command(bookmark_group)
