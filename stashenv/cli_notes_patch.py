"""Registers the notes command group into the main CLI."""

from stashenv.cli_notes import register


def apply_patch(cli):
    """Call this from the main cli entrypoint to attach the notes group."""
    register(cli)
