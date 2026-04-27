"""CLI commands for copying/cloning profiles."""

import click
from stashenv.store import _store_dir
from stashenv.copy import copy_profile, ProfileNotFoundError, ProfileAlreadyExistsError


@click.group("copy")
def copy_group():
    """Copy and clone profile commands."""


@copy_group.command("profile")
@click.argument("source")
@click.argument("destination")
@click.option("--store", "store_dir", default=None, help="Path to store directory.")
def copy_cmd(source: str, destination: str, store_dir):
    """Copy SOURCE profile to a new DESTINATION profile.

    The destination profile will be encrypted with the same password
    as the source — use the original password to load it.
    """
    store = _store_dir(store_dir)
    try:
        copy_profile(store, source, destination)
        click.echo(f"Profile '{source}' copied to '{destination}'.")
    except ProfileNotFoundError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
    except ProfileAlreadyExistsError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
    except ValueError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


def register(cli):
    """Register the copy group with the main CLI."""
    cli.add_command(copy_group)
