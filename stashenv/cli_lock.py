"""CLI commands for locking and unlocking profiles."""

import click
from pathlib import Path
from stashenv.store import _store_dir
from stashenv.lock import lock_profile, unlock_profile, list_locked, is_locked


@click.group("lock")
def lock_group():
    """Lock or unlock profiles to prevent accidental changes."""


@lock_group.command("add")
@click.argument("profile")
def lock_cmd(profile: str):
    """Lock a profile."""
    store = _store_dir()
    if is_locked(store, profile):
        click.echo(f"Profile '{profile}' is already locked.")
        return
    lock_profile(store, profile)
    click.echo(f"Profile '{profile}' locked.")


@lock_group.command("remove")
@click.argument("profile")
def unlock_cmd(profile: str):
    """Unlock a profile."""
    store = _store_dir()
    if not is_locked(store, profile):
        click.echo(f"Profile '{profile}' is not locked.")
        return
    unlock_profile(store, profile)
    click.echo(f"Profile '{profile}' unlocked.")


@lock_group.command("list")
def list_cmd():
    """List all locked profiles."""
    store = _store_dir()
    locked = list_locked(store)
    if not locked:
        click.echo("No profiles are currently locked.")
        return
    for name in locked:
        click.echo(f"  🔒 {name}")


def register(cli: click.Group) -> None:
    cli.add_command(lock_group)
