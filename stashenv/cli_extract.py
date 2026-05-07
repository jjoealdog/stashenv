"""CLI commands for extracting keys from a profile into a new profile."""

from __future__ import annotations

import click

from stashenv.env_extract import (
    NoKeysMatchedError,
    ProfileNotFoundError,
    extract_profile,
)


@click.group("extract")
def extract_group() -> None:
    """Extract keys from a profile into a new profile."""


@extract_group.command("run")
@click.argument("source")
@click.argument("destination")
@click.option("-k", "--key", "keys", multiple=True, required=True, help="Key to extract (repeatable).")
@click.option("--password", prompt=True, hide_input=True, help="Profile password.")
@click.option("--strict", is_flag=True, default=False, help="Fail if no keys match.")
def run_cmd(source: str, destination: str, keys: tuple, password: str, strict: bool) -> None:
    """Extract KEY(s) from SOURCE into DESTINATION profile."""
    try:
        result = extract_profile(
            source,
            destination,
            list(keys),
            password,
            strict=strict,
        )
    except ProfileNotFoundError as exc:
        raise click.ClickException(str(exc))
    except NoKeysMatchedError as exc:
        raise click.ClickException(str(exc))

    click.echo(
        f"Extracted {result.total_extracted} key(s) from '{source}' "
        f"into '{destination}'."
    )
    if result.skipped_keys:
        click.echo(f"Skipped (not found): {', '.join(result.skipped_keys)}")


def register(cli: click.Group) -> None:  # pragma: no cover
    """Attach the extract command group to *cli*."""
    cli.add_command(extract_group)
