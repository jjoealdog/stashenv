"""CLI commands for exporting and importing stashenv profile bundles."""

import click
from pathlib import Path

from stashenv.export import export_profile, import_profile, export_all_profiles


@click.group()
def export_group():
    """Export and import profile bundles."""


@export_group.command("export")
@click.argument("project")
@click.argument("profile")
@click.option(
    "--dest",
    "-d",
    default=".",
    show_default=True,
    help="Destination directory for the bundle file.",
)
def export_cmd(project: str, profile: str, dest: str):
    """Export a single profile to a portable bundle file."""
    dest_path = Path(dest)
    try:
        out = export_profile(project, profile, dest_path)
        click.echo(f"Exported to {out}")
    except FileNotFoundError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)


@export_group.command("export-all")
@click.argument("project")
@click.option("--dest", "-d", default=".", show_default=True)
def export_all_cmd(project: str, dest: str):
    """Export all profiles for a project."""
    dest_path = Path(dest)
    try:
        paths = export_all_profiles(project, dest_path)
        for p in paths:
            click.echo(f"Exported {p.name}")
    except (FileNotFoundError, ValueError) as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)


@export_group.command("import")
@click.argument("bundle", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--project",
    "-p",
    default=None,
    help="Override the project name from the bundle.",
)
def import_cmd(bundle: Path, project: str | None):
    """Import a profile bundle into the local store."""
    try:
        proj, prof = import_profile(bundle, dest_project=project)
        click.echo(f"Imported profile '{prof}' into project '{proj}'")
    except (FileNotFoundError, Exception) as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)
