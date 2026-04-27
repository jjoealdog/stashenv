"""Patch save_profile and delete_profile to respect profile locks."""

from pathlib import Path
from stashenv import store as _store_module
from stashenv.lock import is_locked, ProfileLockedError


_original_save = _store_module.save_profile
_original_delete = _store_module.delete_profile


def save_profile(store_dir: Path, profile: str, plaintext: str, password: str) -> None:
    """Save a profile, raising ProfileLockedError if it is locked."""
    if is_locked(store_dir, profile):
        raise ProfileLockedError(
            f"Profile '{profile}' is locked. Unlock it before saving."
        )
    _original_save(store_dir, profile, plaintext, password)


def delete_profile(store_dir: Path, profile: str) -> None:
    """Delete a profile, raising ProfileLockedError if it is locked."""
    if is_locked(store_dir, profile):
        raise ProfileLockedError(
            f"Profile '{profile}' is locked. Unlock it before deleting."
        )
    _original_delete(store_dir, profile)


def apply_patch() -> None:
    """Replace store module functions with lock-aware versions."""
    _store_module.save_profile = save_profile
    _store_module.delete_profile = delete_profile
