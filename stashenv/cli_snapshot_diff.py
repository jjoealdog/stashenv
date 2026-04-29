"""CLI commands for diffing a profile against one of its snapshots."""

import click
from pathlib import Path

from stashenv.snapshot_diff import (
    diff_against_snapshot,
    format_snapshot_diff,
    SnapshotNotFoundError,
    ProfileNotFoundError,
)
from stashenv.store import _store_dir


@click.group("snapshot-diff")
def snapshot_diff_group():
    """Diff a profile against a historical snapshot."""


@snapshot_diff_group.command("show")
@click.argument("profile")
@click.argument("version", type=int)
@click.option("--password", prompt=True, hide_input=True, help="Encryption password")
@click.option("--show-values", is_flag=True, default=False, help="Show actual values")
def show_cmd(profile: str, version: int, password: str, show_values: bool):
    """Show diff between PROFILE's current state and snapshot VERSION."""
    store = _store_dir()
    try:
        entries = diff_against_snapshot(store, profile, password, version, show_values)
    except SnapshotNotFoundError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)
    except ProfileNotFoundError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)

    output = format_snapshot_diff(entries, profile, version, show_values=show_values)
    click.echo(output)


def register(cli):
    cli.add_command(snapshot_diff_group)
