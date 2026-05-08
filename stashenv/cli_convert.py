"""CLI commands for converting profiles to/from different formats."""

from __future__ import annotations

import sys
from pathlib import Path

import click

from stashenv.env_convert import (
    export_as,
    import_from,
    UnsupportedFormatError,
    SUPPORTED_FORMATS,
)
from stashenv.store import _store_dir


@click.group("convert")
def convert_group():
    """Convert profiles between dotenv, JSON, and YAML formats."""


@convert_group.command("export")
@click.argument("profile")
@click.option("--password", "-p", prompt=True, hide_input=True, help="Profile password")
@click.option(
    "--format", "-f", "fmt",
    default="dotenv",
    show_default=True,
    type=click.Choice(SUPPORTED_FORMATS),
    help="Output format",
)
@click.option("--output", "-o", "output_path", default=None, help="Write to file instead of stdout")
def export_cmd(profile: str, password: str, fmt: str, output_path: str | None):
    """Export a profile as dotenv, JSON, or YAML."""
    store = _store_dir()
    try:
        text = export_as(store, profile, password, fmt)
    except UnsupportedFormatError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)
    except FileNotFoundError:
        click.echo(f"Error: profile '{profile}' not found.", err=True)
        sys.exit(1)
    except Exception as exc:  # noqa: BLE001
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)

    if output_path:
        Path(output_path).write_text(text)
        click.echo(f"Exported '{profile}' ({fmt}) -> {output_path}")
    else:
        click.echo(text, nl=False)


@convert_group.command("import")
@click.argument("profile")
@click.argument("input_file", type=click.Path(exists=True, dir_okay=False))
@click.option("--password", "-p", prompt=True, hide_input=True, confirmation_prompt=True)
@click.option(
    "--format", "-f", "fmt",
    default="dotenv",
    show_default=True,
    type=click.Choice(SUPPORTED_FORMATS),
    help="Input format",
)
def import_cmd(profile: str, input_file: str, password: str, fmt: str):
    """Import a profile from a dotenv, JSON, or YAML file."""
    store = _store_dir()
    text = Path(input_file).read_text()
    try:
        import_from(store, profile, password, text, fmt)
    except UnsupportedFormatError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)
    except ValueError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)
    except Exception as exc:  # noqa: BLE001
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)

    click.echo(f"Imported '{profile}' from {input_file} ({fmt}).")


def register(cli: click.Group) -> None:
    cli.add_command(convert_group)
