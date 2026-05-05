"""CLI commands for archiving and restoring profile sets."""

from __future__ import annotations

from pathlib import Path

import click

from stashenv.archive import (
    archive_profiles,
    restore_profiles,
    ArchiveError,
    ProfileNotFoundError,
)
from stashenv.store import _store_dir


@click.group("archive")
def archive_group():
    """Archive and restore profile sets."""


@archive_group.command("create")
@click.argument("dest")
@click.option(
    "--profile",
    "profiles",
    multiple=True,
    help="Profile name(s) to include. Defaults to all.",
)
@click.pass_context
def create_cmd(ctx, dest: str, profiles: tuple[str, ...]):
    """Create a compressed archive of profiles."""
    store_dir = _store_dir(ctx.obj.get("project_dir", Path.cwd()))
    out = Path(dest)
    try:
        names = archive_profiles(
            store_dir,
            out,
            profiles=list(profiles) if profiles else None,
        )
    except ProfileNotFoundError as exc:
        click.echo(f"Error: {exc}", err=True)
        ctx.exit(1)
    except ArchiveError as exc:
        click.echo(f"Error: {exc}", err=True)
        ctx.exit(1)
    else:
        click.echo(f"Archived {len(names)} profile(s) to {out}")
        for name in sorted(names):
            click.echo(f"  - {name}")


@archive_group.command("restore")
@click.argument("src")
@click.option(
    "--overwrite",
    is_flag=True,
    default=False,
    help="Overwrite existing profiles.",
)
@click.pass_context
def restore_cmd(ctx, src: str, overwrite: bool):
    """Restore profiles from an archive."""
    store_dir = _store_dir(ctx.obj.get("project_dir", Path.cwd()))
    archive_path = Path(src)
    try:
        names = restore_profiles(store_dir, archive_path, overwrite=overwrite)
    except ArchiveError as exc:
        click.echo(f"Error: {exc}", err=True)
        ctx.exit(1)
    else:
        click.echo(f"Restored {len(names)} profile(s) from {archive_path}")
        for name in sorted(names):
            click.echo(f"  - {name}")


def register(cli: click.Group):
    cli.add_command(archive_group)
