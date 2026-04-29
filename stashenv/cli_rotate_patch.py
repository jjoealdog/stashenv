"""Patch to register the rotate group with the main CLI."""

import click
from stashenv.cli_rotate import register


def apply_patch(cli: click.Group) -> None:
    """Register rotate commands onto the given CLI group."""
    register(cli)
