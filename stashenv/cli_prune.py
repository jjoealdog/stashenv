"""CLI commands for pruning stale profiles."""

from __future__ import annotations

import click

from stashenv.prune import prune_expired, prune_older_than


@click.group("prune")
def prune_group():
    """Remove stale or expired profiles."""


@prune_group.command("expired")
@click.option("--dry-run", is_flag=True, default=False, help="Show what would be removed without deleting.")
@click.pass_context
def expired_cmd(ctx, dry_run):
    """Delete all profiles whose expiry date has passed."""
    store_dir = ctx.obj.get("store_dir") if ctx.obj else None
    kwargs = {"store_dir": store_dir} if store_dir else {}

    if dry_run:
        # preview only — import list_profiles and expire helpers
        from datetime import datetime, timezone
        from stashenv.store import list_profiles, _store_dir
        from stashenv.expire import get_expiry
        sd = store_dir or _store_dir()
        now = datetime.now(tz=timezone.utc)
        found = [n for n in list_profiles(sd) if (e := get_expiry(sd, n)) and e <= now]
        if not found:
            click.echo("No expired profiles found.")
        else:
            click.echo("Would prune:")
            for name in found:
                click.echo(f"  {name}")
        return

    result = prune_expired(**kwargs)
    if not result.pruned:
        click.echo("No expired profiles found.")
    else:
        for name in result.pruned:
            click.echo(f"Pruned: {name}")
        click.echo(f"\n{result.total} profile(s) removed.")


@prune_group.command("old")
@click.argument("days", type=int)
@click.option("--dry-run", is_flag=True, default=False, help="Show what would be removed without deleting.")
@click.pass_context
def old_cmd(ctx, days, dry_run):
    """Delete profiles not modified in the last DAYS days."""
    store_dir = ctx.obj.get("store_dir") if ctx.obj else None
    kwargs = {"store_dir": store_dir} if store_dir else {}

    if dry_run:
        from datetime import datetime, timedelta, timezone
        from stashenv.store import list_profiles, _store_dir
        from stashenv.prune import _profile_mtime
        sd = store_dir or _store_dir()
        cutoff = datetime.now(tz=timezone.utc) - timedelta(days=days)
        found = [n for n in list_profiles(sd) if (m := _profile_mtime(sd, n)) and m < cutoff]
        if not found:
            click.echo(f"No profiles older than {days} day(s) found.")
        else:
            click.echo("Would prune:")
            for name in found:
                click.echo(f"  {name}")
        return

    result = prune_older_than(days=days, **kwargs)
    if not result.pruned:
        click.echo(f"No profiles older than {days} day(s) found.")
    else:
        for name in result.pruned:
            click.echo(f"Pruned: {name}")
        click.echo(f"\n{result.total} profile(s) removed.")


def register(cli):
    cli.add_command(prune_group)
