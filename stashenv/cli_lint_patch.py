"""Register the lint command group with the main CLI."""
from stashenv.cli_lint import register


def apply_patch(cli):
    register(cli)
