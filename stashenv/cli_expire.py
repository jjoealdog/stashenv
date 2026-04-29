"""CLI commands for managing profile expiry."""

from datetime import datetime, timezone
from pathlib import Path

import click

from stashenv.expire import (
    set_expiry,
    clear_expiry,
    get_expiry,
    list_expiry,
    ProfileExpiredError,
)
from stashenv.store import _store_dir


@click.group("expire")
def expire_group():
    """Manage profile expiry dates."""


@expire_group.command("set")
@click.argument("profile")
@click.argument("expires_at")  # ISO 8601 string, e.g. 2025-12-31T23:59:59
def set_cmd(profile: str, expires_at: str):
    """Set an expiry date for PROFILE (ISO 8601 UTC datetime)."""
    try:
        dt = datetime.fromisoformat(expires_at)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
    except ValueError:
        click.echo(f"Error: invalid datetime '{expires_at}'. Use ISO 8601 format.", err=True)
        raise SystemExit(1)

    store = _store_dir()
    set_expiry(store, profile, dt)
    click.echo(f"Expiry for '{profile}' set to {dt.isoformat()}.")


@expire_group.command("clear")
@click.argument("profile")
def clear_cmd(profile: str):
    """Remove expiry date from PROFILE."""
    store = _store_dir()
    removed = clear_expiry(store, profile)
    if removed:
        click.echo(f"Expiry for '{profile}' cleared.")
    else:
        click.echo(f"No expiry was set for '{profile}'.")


@expire_group.command("get")
@click.argument("profile")
def get_cmd(profile: str):
    """Show expiry date for PROFILE."""
    store = _store_dir()
    expiry = get_expiry(store, profile)
    if expiry is None:
        click.echo(f"No expiry set for '{profile}'.")
    else:
        now = datetime.now(timezone.utc)
        status = "EXPIRED" if now >= expiry else "active"
        click.echo(f"{profile}: {expiry.isoformat()} [{status}]")


@expire_group.command("list")
def list_cmd():
    """List all profiles with expiry dates."""
    store = _store_dir()
    entries = list_expiry(store)
    if not entries:
        click.echo("No expiry dates set.")
        return
    now = datetime.now(timezone.utc)
    for name, expiry in sorted(entries.items()):
        status = "EXPIRED" if now >= expiry else "active"
        click.echo(f"  {name:<20} {expiry.isoformat()}  [{status}]")


def register(cli):
    cli.add_command(expire_group)
