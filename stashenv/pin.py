"""Pin a profile as the default for the current project directory."""

import json
from pathlib import Path

_PIN_FILENAME = ".stashenv-pin"


def _pin_path(project_dir: Path | None = None) -> Path:
    base = project_dir or Path.cwd()
    return base / _PIN_FILENAME


def pin_profile(profile_name: str, project_dir: Path | None = None) -> Path:
    """Pin a profile name as the default for the given directory."""
    if not profile_name or not profile_name.strip():
        raise ValueError("Profile name must not be empty.")
    pin_file = _pin_path(project_dir)
    data = {"profile": profile_name.strip()}
    pin_file.write_text(json.dumps(data) + "\n", encoding="utf-8")
    return pin_file


def unpin_profile(project_dir: Path | None = None) -> bool:
    """Remove the pinned profile for the given directory.

    Returns True if a pin file was removed, False if none existed.
    """
    pin_file = _pin_path(project_dir)
    if pin_file.exists():
        pin_file.unlink()
        return True
    return False


def get_pinned_profile(project_dir: Path | None = None) -> str | None:
    """Return the pinned profile name, or None if no pin is set."""
    pin_file = _pin_path(project_dir)
    if not pin_file.exists():
        return None
    try:
        data = json.loads(pin_file.read_text(encoding="utf-8"))
        return data.get("profile")
    except (json.JSONDecodeError, KeyError):
        return None
