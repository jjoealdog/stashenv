"""CLI commands for profile version history."""

import click
from datetime import datetime
from pathlib import Path

from stashenv.store import _store_dir, _profile_path, load_profile
from stashenv.history import list_snapshots, get_snapshot, clear_history
from stashenv.crypto import decrypt


@click.group(name="history")
def history_group():
    """Manage profile version history."""


@history_group.command(name="list")
@click.argument("profile")
def list_cmd(profile: str):
    """List saved snapshots for a profile."""
    store = _store_dir()
    snaps = list_snapshots(store, profile)
    if not snaps:
        click.echo(f"No history for profile '{profile}'.")
        return
    click.echo(f"History for '{profile}' ({len(snaps)} snapshot(s)):")
    for s in snaps:
        ts = datetime.fromtimestamp(s["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
        note = f"  # {s['note']}" if s["note"] else ""
        click.echo(f"  v{s['version']}  {ts}{note}")


@history_group.command(name="restore")
@click.argument("profile")
@click.argument("version", type=int)
@click.option("--password", prompt=True, hide_input=True, help="Encryption password.")
def restore_cmd(profile: str, version: int, password: str):
    """Restore a profile to a previous snapshot version."""
    store = _store_dir()
    data = get_snapshot(store, profile, version)
    if data is None:
        click.echo(f"Snapshot v{version} not found for profile '{profile}'.", err=True)
        raise SystemExit(1)
    try:
        plaintext = decrypt(data, password)
    except Exception:
        click.echo("Decryption failed — wrong password?", err=True)
        raise SystemExit(1)

    profile_path = _profile_path(store, profile)
    profile_path.write_bytes(data)
    click.echo(f"Restored '{profile}' to v{version}. ({len(plaintext)} bytes of env data)")


@history_group.command(name="clear")
@click.argument("profile")
@click.confirmation_option(prompt="Delete all history for this profile?")
def clear_cmd(profile: str):
    """Delete all history snapshots for a profile."""
    store = _store_dir()
    removed = clear_history(store, profile)
    click.echo(f"Cleared {removed} snapshot(s) for '{profile}'.")


def register(cli):
    cli.add_command(history_group)
