"""Patch to register the diff group into the main CLI."""

from __future__ import annotations

from stashenv.cli import cli
from stashenv.cli_diff import diff_group


def register() -> None:
    """Attach the diff command group to the root CLI."""
    cli.add_command(diff_group, name="diff")


if __name__ == "__main__":
    register()
    cli()
