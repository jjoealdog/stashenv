"""CLI commands for formatting .env profiles."""
from __future__ import annotations

import click

from stashenv.fmt import format_env_text
from stashenv.store import _store_dir, _profile_path


@click.group("fmt")
def fmt_group() -> None:
    """Format and normalise stored .env profiles."""


@fmt_group.command("run")
@click.argument("profile")
@click.option("--sort", is_flag=True, default=False, help="Sort keys alphabetically.")
@click.option("--strip-comments", is_flag=True, default=False, help="Remove inline comments.")
@click.option("--check", is_flag=True, default=False, help="Exit non-zero if formatting would change the file.")
@click.option("--password", prompt=True, hide_input=True, help="Profile password.")
@click.pass_context
def run_cmd(ctx: click.Context, profile: str, sort: bool, strip_comments: bool, check: bool, password: str) -> None:
    """Format a stored profile in-place."""
    from stashenv.store import load_profile, save_profile

    store = ctx.obj.get("store") if ctx.obj else None
    try:
        raw = load_profile(profile, password, store_dir=store)
    except FileNotFoundError:
        click.echo(f"error: profile '{profile}' not found", err=True)
        ctx.exit(1)
        return
    except ValueError:
        click.echo("error: wrong password", err=True)
        ctx.exit(1)
        return

    result = format_env_text(raw, sort_keys=sort, strip_inline_comments=strip_comments)

    if check:
        if result.changed:
            click.echo(f"profile '{profile}' is not formatted")
            ctx.exit(1)
        else:
            click.echo(f"profile '{profile}' is already formatted")
        return

    if not result.changed:
        click.echo(f"profile '{profile}' is already formatted — nothing to do")
        return

    save_profile(profile, result.formatted, password, store_dir=store)
    click.echo(f"formatted profile '{profile}'")
    for change in result.changes:
        click.echo(f"  · {change}")


@fmt_group.command("file")
@click.argument("path", type=click.Path(exists=True))
@click.option("--sort", is_flag=True, default=False)
@click.option("--strip-comments", is_flag=True, default=False)
@click.option("--check", is_flag=True, default=False)
@click.option("--write", is_flag=True, default=False, help="Write result back to file.")
def file_cmd(path: str, sort: bool, strip_comments: bool, check: bool, write: bool) -> None:
    """Format a plain .env file on disk."""
    with open(path, "r") as fh:
        original = fh.read()

    result = format_env_text(original, sort_keys=sort, strip_inline_comments=strip_comments)

    if check:
        if result.changed:
            click.echo(f"{path}: would reformat")
            raise SystemExit(1)
        click.echo(f"{path}: ok")
        return

    if write:
        with open(path, "w") as fh:
            fh.write(result.formatted)
        click.echo(f"wrote formatted output to {path}")
    else:
        click.echo(result.formatted, nl=False)


def register(cli: click.Group) -> None:
    cli.add_command(fmt_group)
