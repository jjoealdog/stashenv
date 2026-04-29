"""CLI commands for merging profiles."""
from __future__ import annotations

from pathlib import Path

import click

from stashenv.merge import (
    merge_profiles,
    MergeStrategy,
    ProfileNotFoundError,
    ProfileAlreadyExistsError,
)
from stashenv.store import _store_dir


@click.group("merge")
def merge_group() -> None:
    """Merge two profiles into a new profile."""


@merge_group.command("run")
@click.argument("base")
@click.argument("override")
@click.argument("destination")
@click.option("--base-password", prompt=True, hide_input=True, help="Password for base profile")
@click.option("--override-password", prompt=True, hide_input=True, help="Password for override profile")
@click.option("--dest-password", prompt=True, hide_input=True, confirmation_prompt=True, help="Password for destination profile")
@click.option(
    "--strategy",
    type=click.Choice(["base", "override", "union"]),
    default="override",
    show_default=True,
    help="Conflict resolution strategy",
)
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite destination if it exists")
@click.pass_context
def merge_cmd(
    ctx: click.Context,
    base: str,
    override: str,
    destination: str,
    base_password: str,
    override_password: str,
    dest_password: str,
    strategy: str,
    overwrite: bool,
) -> None:
    """Merge BASE and OVERRIDE profiles into DESTINATION."""
    store_dir: Path = ctx.obj.get("store_dir", _store_dir())
    try:
        count = merge_profiles(
            store_dir,
            base,
            override,
            destination,
            base_password,
            override_password,
            dest_password,
            strategy=strategy,  # type: ignore[arg-type]
            overwrite=overwrite,
        )
        click.echo(f"Merged '{base}' + '{override}' → '{destination}' ({count} keys, strategy={strategy})")
    except ProfileNotFoundError as exc:
        click.echo(f"Error: {exc}", err=True)
        ctx.exit(1)
    except ProfileAlreadyExistsError as exc:
        click.echo(f"Error: {exc}", err=True)
        ctx.exit(1)


def register(cli: click.Group) -> None:
    cli.add_command(merge_group)
