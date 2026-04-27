"""Profile rename functionality for stashenv."""

from pathlib import Path
from stashenv.store import _profile_path, _store_dir, list_profiles


class ProfileNotFoundError(FileNotFoundError):
    pass


class ProfileAlreadyExistsError(FileExistsError):
    pass


def rename_profile(store_dir: Path, old_name: str, new_name: str) -> None:
    """Rename a stored profile from old_name to new_name.

    Raises:
        ProfileNotFoundError: if old_name does not exist.
        ProfileAlreadyExistsError: if new_name already exists.
        ValueError: if either name is empty or contains path separators.
    """
    for name in (old_name, new_name):
        if not name or not name.strip():
            raise ValueError(f"Profile name must not be empty: {name!r}")
        if "/" in name or "\\" in name:
            raise ValueError(f"Profile name must not contain path separators: {name!r}")

    old_path = _profile_path(store_dir, old_name)
    new_path = _profile_path(store_dir, new_name)

    if not old_path.exists():
        raise ProfileNotFoundError(f"Profile not found: {old_name!r}")

    if new_path.exists():
        raise ProfileAlreadyExistsError(f"Profile already exists: {new_name!r}")

    old_path.rename(new_path)
