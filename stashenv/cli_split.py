"""CLI commands for splitting a profile into multiple sub-profiles."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import click

from stashenv.env_split import split_profile, ProfileNotFoundError, SplitError
from stashenv.store import _store_dir


@click.group("split")
def split_group():
    """Split a profile into multiple smaller profiles."""


@split_group.command("run")
@click.argument("source")
@click.option("-p", "--password", prompt=True, hide_input=True, help="Profile password.")
@click.option(
    "-g",
    "--group",
    "groups",
    multiple=True,
    metavar="NAME:KEY1,KEY2,...",
    required=True,
    help="Destination profile and keys, e.g. db:DB_HOST,DB_PORT",
)
@click.option(
    "-r",
    "--remainder",
    "remainder_profile",
    default=None,
    help="Profile name to receive unassigned keys.",
)
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing profiles.")
@click.option("--store", "store_path", default=None, help="Override store directory.")
def run_cmd(
    source: str,
    password: str,
    groups: tuple,
    remainder_profile: Optional[str],
    overwrite: bool,
    store_path: Optional[str],
):
    """Split SOURCE profile into destination profiles defined by --group options."""
    store_dir = Path(store_path) if store_path else _store_dir()

    parsed_groups: dict = {}
    for entry in groups:
        if ":" not in entry:
            click.echo(f"Invalid group format '{entry}'. Expected NAME:KEY1,KEY2,...", err=True)
            sys.exit(1)
        name, _, keys_str = entry.partition(":")
        parsed_groups[name.strip()] = [k.strip() for k in keys_str.split(",") if k.strip()]

    try:
        result = split_profile(
            store_dir,
            source,
            password,
            parsed_groups,
            remainder_profile=remainder_profile,
            overwrite=overwrite,
        )
    except ProfileNotFoundError as exc:
        click.echo(str(exc), err=True)
        sys.exit(1)
    except SplitError as exc:
        click.echo(str(exc), err=True)
        sys.exit(1)

    click.echo(f"Split '{result.source}' into {len(result.destinations)} profile(s):")
    for dest in result.destinations:
        click.echo(f"  - {dest}")
    click.echo(f"{result.keys_placed}/{result.total_keys} keys placed ({result.unplaced} unplaced).")


def register(cli: click.Group) -> None:
    cli.add_command(split_group)
