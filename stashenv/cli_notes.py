"""CLI commands for managing per-profile notes."""

import click
from stashenv.notes import set_note, get_note, remove_note, list_notes
from stashenv.store import _store_dir, list_profiles


@click.group(name="notes")
def notes_group():
    """Manage notes attached to profiles."""
    pass


@notes_group.command(name="set")
@click.argument("profile")
@click.argument("text")
def set_cmd(profile, text):
    """Set or replace the note for PROFILE."""
    store_dir = _store_dir()
    profiles = list_profiles(store_dir)
    if profile not in profiles:
        click.echo(f"Profile '{profile}' not found.", err=True)
        raise SystemExit(1)
    set_note(profile, text, store_dir=store_dir)
    click.echo(f"Note set for profile '{profile}'.")


@notes_group.command(name="get")
@click.argument("profile")
def get_cmd(profile):
    """Show the note for PROFILE."""
    store_dir = _store_dir()
    note = get_note(profile, store_dir=store_dir)
    if note is None:
        click.echo(f"No note set for profile '{profile}'.")
    else:
        click.echo(note)


@notes_group.command(name="remove")
@click.argument("profile")
def remove_cmd(profile):
    """Remove the note for PROFILE."""
    store_dir = _store_dir()
    removed = remove_note(profile, store_dir=store_dir)
    if removed:
        click.echo(f"Note removed for profile '{profile}'.")
    else:
        click.echo(f"No note found for profile '{profile}'.")


@notes_group.command(name="list")
def list_cmd():
    """List all profiles that have notes."""
    store_dir = _store_dir()
    all_notes = list_notes(store_dir=store_dir)
    if not all_notes:
        click.echo("No notes found.")
        return
    for profile, text in sorted(all_notes.items()):
        click.echo(f"{profile}: {text}")


def register(cli):
    cli.add_command(notes_group)
