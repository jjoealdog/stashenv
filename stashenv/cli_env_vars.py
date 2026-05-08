"""CLI commands for variable interpolation."""

from __future__ import annotations

from pathlib import Path

import click

from stashenv.env_vars import UnresolvedVariableError, interpolate_profile


@click.group("vars")
def vars_group() -> None:
    """Interpolate variable references within a profile."""


@vars_group.command("expand")
@click.argument("profile")
@click.option("--password", prompt=True, hide_input=True, help="Profile password.")
@click.option(
    "--store",
    default=None,
    type=click.Path(file_okay=False),
    help="Override store directory.",
)
@click.option(
    "--strict",
    is_flag=True,
    default=False,
    help="Exit non-zero if any variable reference is unresolved.",
)
@click.option(
    "--set",
    "extra",
    multiple=True,
    metavar="KEY=VALUE",
    help="Extra context variables (repeatable).",
)
def expand_cmd(
    profile: str,
    password: str,
    store: str | None,
    strict: bool,
    extra: tuple[str, ...],
) -> None:
    """Print interpolated key=value pairs for PROFILE."""
    from stashenv.store import _store_dir

    store_path = Path(store) if store else _store_dir()

    context: dict[str, str] = {}
    for item in extra:
        if "=" not in item:
            raise click.BadParameter(f"Expected KEY=VALUE, got: {item!r}", param_hint="--set")
        k, _, v = item.partition("=")
        context[k.strip()] = v.strip()

    try:
        result = interpolate_profile(profile, password, store_path, context=context, strict=strict)
    except UnresolvedVariableError as exc:
        raise click.ClickException(str(exc)) from exc
    except FileNotFoundError:
        raise click.ClickException(f"Profile '{profile}' not found.")

    for key, value in result.expanded.items():
        click.echo(f"{key}={value}")

    if not result.ok and not strict:
        click.echo(
            f"\nWarning: {len(result.unresolved)} unresolved reference(s): "
            + ", ".join(result.unresolved),
            err=True,
        )


def register(cli: click.Group) -> None:
    cli.add_command(vars_group)
