"""CLI commands for managing profile TTLs."""

from __future__ import annotations

import click

from stashenv.store import _store_dir
from stashenv.ttl import (
    TTLExpiredError,
    clear_ttl,
    get_ttl,
    list_ttl,
    set_ttl,
)


@click.group("ttl")
def ttl_group() -> None:
    """Manage per-profile time-to-live settings."""


@ttl_group.command("set")
@click.argument("profile")
@click.argument("seconds", type=int)
def set_cmd(profile: str, seconds: int) -> None:
    """Set a TTL of SECONDS for PROFILE."""
    if seconds <= 0:
        raise click.ClickException("TTL must be a positive integer.")
    store = _store_dir()
    set_ttl(store, profile, seconds)
    click.echo(f"TTL for '{profile}' set to {seconds}s.")


@ttl_group.command("clear")
@click.argument("profile")
def clear_cmd(profile: str) -> None:
    """Remove the TTL from PROFILE."""
    store = _store_dir()
    clear_ttl(store, profile)
    click.echo(f"TTL cleared for '{profile}'.")


@ttl_group.command("get")
@click.argument("profile")
def get_cmd(profile: str) -> None:
    """Show the TTL record for PROFILE."""
    store = _store_dir()
    rec = get_ttl(store, profile)
    if rec is None:
        click.echo(f"No TTL set for '{profile}'.")
        return
    import time
    elapsed = time.time() - rec["created_at"]
    remaining = max(0.0, rec["ttl"] - elapsed)
    stale = "(stale)" if elapsed > rec["ttl"] else ""
    click.echo(f"profile : {profile}")
    click.echo(f"ttl     : {rec['ttl']}s")
    click.echo(f"remaining: {remaining:.0f}s {stale}".rstrip())


@ttl_group.command("list")
def list_cmd() -> None:
    """List all profiles with a TTL set."""
    store = _store_dir()
    rows = list_ttl(store)
    if not rows:
        click.echo("No TTL entries found.")
        return
    click.echo(f"{'PROFILE':<20} {'TTL':>8}  {'REMAINING':>10}  STATUS")
    click.echo("-" * 52)
    for r in rows:
        status = "STALE" if r["stale"] else "ok"
        click.echo(
            f"{r['profile']:<20} {r['ttl']:>8}s {r['remaining']:>9.0f}s  {status}"
        )


def register(cli: click.Group) -> None:
    cli.add_command(ttl_group)
