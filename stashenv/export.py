"""Utilities for exporting and importing env profiles as portable bundles."""

import json
import base64
from pathlib import Path
from stashenv.store import _profile_path, list_profiles


def export_profile(project: str, profile: str, dest: Path) -> Path:
    """Export an encrypted profile to a portable .stashenv bundle file.

    The bundle is a base64-encoded JSON file containing project, profile name,
    and the raw encrypted bytes. The password is NOT included.

    Returns the path to the written bundle file.
    """
    src = _profile_path(project, profile)
    if not src.exists():
        raise FileNotFoundError(f"Profile '{profile}' not found for project '{project}'")

    raw = src.read_bytes()
    bundle = {
        "project": project,
        "profile": profile,
        "data": base64.b64encode(raw).decode("utf-8"),
    }

    dest.mkdir(parents=True, exist_ok=True)
    out_path = dest / f"{project}__{profile}.stashenv"
    out_path.write_text(json.dumps(bundle, indent=2))
    return out_path


def import_profile(bundle_path: Path, dest_project: str | None = None) -> tuple[str, str]:
    """Import a .stashenv bundle file into the local store.

    If dest_project is provided it overrides the project name stored in the bundle.
    Returns (project, profile) tuple of the imported entry.

    Raises:
        FileNotFoundError: If the bundle file does not exist.
        ValueError: If the bundle file is missing required fields or contains invalid data.
    """
    if not bundle_path.exists():
        raise FileNotFoundError(f"Bundle file not found: {bundle_path}")

    try:
        bundle = json.loads(bundle_path.read_text())
    except json.JSONDecodeError as e:
        raise ValueError(f"Bundle file is not valid JSON: {bundle_path}") from e

    missing = [field for field in ("project", "profile", "data") if field not in bundle]
    if missing:
        raise ValueError(f"Bundle file is missing required fields: {', '.join(missing)}")

    project = dest_project or bundle["project"]
    profile = bundle["profile"]

    try:
        raw = base64.b64decode(bundle["data"])
    except Exception as e:
        raise ValueError(f"Bundle data field contains invalid base64 content") from e

    out_path = _profile_path(project, profile)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(raw)
    return project, profile


def export_all_profiles(project: str, dest: Path) -> list[Path]:
    """Export every profile for a project into the destination directory."""
    profiles = list_profiles(project)
    if not profiles:
        raise ValueError(f"No profiles found for project '{project}'")
    return [export_profile(project, p, dest) for p in profiles]
