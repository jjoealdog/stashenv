"""CLI commands for patching individual keys in a stored env profile."""
from __future__ import annotations

from pathlib import Path

import click

from stashenv.env_patch import patch_profile, ProfileNotFoundError


@click.group("patch")
def patch_group() -> None:
    """Apply key-level mutations to a stored profile."""


@patch_group.command("set")
@click.argument("profile")
@click.argument("assignments", nargs=-1, required=True, metavar="KEY=VALUE...")
@click.option("--password", prompt=True, hide_input=True, help="Profile password.")
@click.pass_context
def set_cmd(ctx: click.Context, profile: str, assignments: tuple[str, ...], password: str) -> None:
    """Set one or more KEY=VALUE pairs in PROFILE."""
    store_dir: Path = ctx.obj["store_dir"]
    set_keys: dict[str, str] = {}
    for item in assignments:
        if "=" not in item:
            raise click.BadParameter(f"Expected KEY=VALUE, got: {item!r}")
        key, _, value = item.partition("=")
        set_keys[key.strip()] = value.strip()

    try:
        result = patch_profile(store_dir, profile, password, set_keys=set_keys)
    except ProfileNotFoundError as exc:
        raise click.ClickException(str(exc))

    for key in result.added:
        click.echo(f"  + {key} (added)")
    for key in result.updated:
        click.echo(f"  ~ {key} (updated)")
    if result.total_changes == 0:
        click.echo("No changes made.")
    else:
        click.echo(f"Patched '{profile}': {result.total_changes} change(s).")


@patch_group.command("remove")
@click.argument("profile")
@click.argument("keys", nargs=-1, required=True, metavar="KEY...")
@click.option("--password", prompt=True, hide_input=True, help="Profile password.")
@click.pass_context
def remove_cmd(ctx: click.Context, profile: str, keys: tuple[str, ...], password: str) -> None:
    """Remove one or more keys from PROFILE."""
    store_dir: Path = ctx.obj["store_dir"]
    try:
        result = patch_profile(store_dir, profile, password, remove_keys=list(keys))
    except ProfileNotFoundError as exc:
        raise click.ClickException(str(exc))

    for key in result.removed:
        click.echo(f"  - {key} (removed)")
    if not result.removed:
        click.echo("No keys removed.")
    else:
        click.echo(f"Patched '{profile}': {len(result.removed)} key(s) removed.")


def register(cli: click.Group) -> None:
    cli.add_command(patch_group)
