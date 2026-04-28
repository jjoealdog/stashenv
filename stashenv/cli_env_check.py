"""CLI commands for validating profiles against a required-keys schema."""

from __future__ import annotations

from pathlib import Path

import click

from stashenv import store
from stashenv.env_check import check_profile, format_check_result, load_required_keys


@click.group(name="check")
def check_group() -> None:
    """Validate profiles against a required-keys schema."""


@check_group.command(name="run")
@click.argument("profile")
@click.option(
    "--schema",
    default=".env.schema",
    show_default=True,
    help="Path to schema file listing required keys (one per line).",
)
@click.option("--password", prompt=True, hide_input=True, help="Decryption password.")
@click.option("--strict", is_flag=True, default=False, help="Exit non-zero if extra keys are found.")
def run_cmd(profile: str, schema: str, password: str, strict: bool) -> None:
    """Check PROFILE against the required-keys schema."""
    schema_path = Path(schema)
    if not schema_path.exists():
        click.echo(f"Schema file not found: {schema}", err=True)
        raise SystemExit(1)

    try:
        env_text = store.load_profile(profile, password)
    except FileNotFoundError:
        click.echo(f"Profile '{profile}' not found.", err=True)
        raise SystemExit(1)
    except Exception as exc:  # noqa: BLE001
        click.echo(f"Error loading profile: {exc}", err=True)
        raise SystemExit(1)

    required_keys = load_required_keys(schema_path)
    result = check_profile(profile, env_text, required_keys)
    click.echo(format_check_result(result))

    if not result.ok:
        raise SystemExit(1)
    if strict and result.extra:
        click.echo("Strict mode: extra keys are not allowed.", err=True)
        raise SystemExit(1)


@check_group.command(name="all")
@click.option(
    "--schema",
    default=".env.schema",
    show_default=True,
    help="Path to schema file.",
)
@click.option("--password", prompt=True, hide_input=True, help="Decryption password.")
def all_cmd(schema: str, password: str) -> None:
    """Check ALL profiles against the required-keys schema."""
    schema_path = Path(schema)
    if not schema_path.exists():
        click.echo(f"Schema file not found: {schema}", err=True)
        raise SystemExit(1)

    profiles = store.list_profiles()
    if not profiles:
        click.echo("No profiles found.")
        return

    required_keys = load_required_keys(schema_path)
    any_failed = False
    for name in profiles:
        try:
            env_text = store.load_profile(name, password)
            result = check_profile(name, env_text, required_keys)
        except Exception as exc:  # noqa: BLE001
            click.echo(f"[ERROR] {name}: {exc}")
            any_failed = True
            continue
        click.echo(format_check_result(result))
        if not result.ok:
            any_failed = True

    if any_failed:
        raise SystemExit(1)


def register(cli: click.Group) -> None:
    cli.add_command(check_group)
