"""Profile locking — prevent accidental overwrites of pinned or protected profiles."""

import json
from pathlib import Path


def _lock_path(store_dir: Path) -> Path:
    return store_dir / ".locks.json"


def _load_locks(store_dir: Path) -> dict:
    p = _lock_path(store_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_locks(store_dir: Path, locks: dict) -> None:
    _lock_path(store_dir).write_text(json.dumps(locks, indent=2))


def lock_profile(store_dir: Path, profile: str) -> None:
    """Mark a profile as locked."""
    locks = _load_locks(store_dir)
    locks[profile] = True
    _save_locks(store_dir, locks)


def unlock_profile(store_dir: Path, profile: str) -> None:
    """Remove the lock from a profile."""
    locks = _load_locks(store_dir)
    locks.pop(profile, None)
    _save_locks(store_dir, locks)


def is_locked(store_dir: Path, profile: str) -> bool:
    """Return True if the profile is currently locked."""
    return _load_locks(store_dir).get(profile, False)


def list_locked(store_dir: Path) -> list[str]:
    """Return a sorted list of all locked profile names."""
    return sorted(k for k, v in _load_locks(store_dir).items() if v)


class ProfileLockedError(Exception):
    """Raised when an operation is attempted on a locked profile."""
