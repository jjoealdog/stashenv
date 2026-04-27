"""CLI commands for interacting with the audit log."""

import click
from pathlib import Path

from stashenv.store import _store_dir
from stashenv.audit import read_events, clear_log


@click.group("audit")
def audit_group():
    """View and manage the audit log."""


@audit_group.command("log")
@click.option("--profile", default=None, help="Filter events by profile name.")
@click.option("--action", default=None, help="Filter events by action (save/load/delete).")
@click.option("--last", default=0, type=int, help="Show only the last N events.")
def log_cmd(profile, action, last):
    """Display audit log entries."""
    store = _store_dir()
    events = read_events(store)

    if profile:
        events = [e for e in events if e["profile"] == profile]
    if action:
        events = [e for e in events if e["action"] == action]
    if last > 0:
        events = events[-last:]

    if not events:
        click.echo("No audit events found.")
        return

    for e in events:
        status = "OK" if e["success"] else "FAIL"
        click.echo(f"{e['ts']}  [{status}]  {e['action']:8s}  {e['profile']}")


@audit_group.command("clear")
@click.confirmation_option(prompt="Are you sure you want to clear the audit log?")
def clear_cmd():
    """Delete the audit log."""
    store = _store_dir()
    clear_log(store)
    click.echo("Audit log cleared.")
