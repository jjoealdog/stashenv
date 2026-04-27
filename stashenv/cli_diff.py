"""CLI commands for diffing .env profiles."""

from __future__ import annotations

import sys

import click

from stashenv.store import load_profile
from stashenv.diff import diff_profiles, format_diff


@click.group("diff")
def diff_group() -> None:
    """Compare two stored .env profiles."""


@diff_group.command("profiles")
@click.argument("profile_a")
@click.argument("profile_b")
@click.option("--password", prompt=True, hide_input=True, help="Decryption password.")
@click.option(
    "--show-values",
    is_flag=True,
    default=False,
    help="Show actual values in diff output.",
)
@click.option(
    "--only",
    type=click.Choice(["added", "removed", "changed", "unchanged"]),
    default=None,
    help="Filter diff output to a specific status.",
)
def diff_cmd(
    profile_a: str,
    profile_b: str,
    password: str,
    show_values: bool,
    only: str | None,
) -> None:
    """Show differences between PROFILE_A and PROFILE_B."""
    try:
        text_a = load_profile(profile_a, password)
    except FileNotFoundError:
        click.echo(f"Profile '{profile_a}' not found.", err=True)
        sys.exit(1)
    except Exception:
        click.echo(f"Failed to decrypt profile '{profile_a}'.", err=True)
        sys.exit(1)

    try:
        text_b = load_profile(profile_b, password)
    except FileNotFoundError:
        click.echo(f"Profile '{profile_b}' not found.", err=True)
        sys.exit(1)
    except Exception:
        click.echo(f"Failed to decrypt profile '{profile_b}'.", err=True)
        sys.exit(1)

    entries = diff_profiles(text_a, text_b, show_values=show_values)

    if only:
        entries = [e for e in entries if e.status == only]

    if not entries:
        click.echo("No differences found.")
        return

    click.echo(f"--- {profile_a}")
    click.echo(f"+++ {profile_b}")
    click.echo(format_diff(entries, show_values=show_values))
