"""Register cli_env_vars with the root CLI."""

from __future__ import annotations

import click


def apply_patch(cli: click.Group) -> None:
    """Attach the vars command group to the root CLI."""
    from stashenv.cli_env_vars import register

    register(cli)
