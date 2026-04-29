"""CLI commands for password rotation."""

import click
from pathlib import Path
from stashenv.store import _store_dir
from stashenv.rotate import (
    rotate_profile,
    rotate_all_profiles,
    ProfileNotFoundError,
    RotationError,
)


@click.group("rotate")
def rotate_group() -> None:
    """Rotate encryption passwords for profiles."""


@rotate_group.command("profile")
@click.argument("profile")
@click.option("--old-password", prompt=True, hide_input=True, help="Current password")
@click.option("--new-password", prompt=True, hide_input=True, confirmation_prompt=True, help="New password")
def rotate_cmd(profile: str, old_password: str, new_password: str) -> None:
    """Re-encrypt PROFILE with a new password."""
    store = _store_dir()
    try:
        rotate_profile(profile, old_password, new_password, store)
        click.echo(f"Password rotated for profile '{profile}'.")
    except ProfileNotFoundError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)
    except RotationError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)


@rotate_group.command("all")
@click.option("--old-password", prompt=True, hide_input=True, help="Current password")
@click.option("--new-password", prompt=True, hide_input=True, confirmation_prompt=True, help="New password")
def rotate_all_cmd(old_password: str, new_password: str) -> None:
    """Re-encrypt all profiles with a new password."""
    store = _store_dir()
    succeeded, failed = rotate_all_profiles(old_password, new_password, store)
    if succeeded:
        click.echo(f"Rotated: {', '.join(succeeded)}")
    if failed:
        click.echo(f"Failed (wrong password?): {', '.join(failed)}", err=True)
    if not succeeded and not failed:
        click.echo("No profiles found.")
    if failed:
        raise SystemExit(1)


def register(cli: click.Group) -> None:
    cli.add_command(rotate_group)
