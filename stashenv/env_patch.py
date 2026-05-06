"""Apply patch-style key updates to a stored env profile."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional

from stashenv.store import load_profile, save_profile


class ProfileNotFoundError(Exception):
    pass


class PatchResult:
    def __init__(self, added: list[str], updated: list[str], removed: list[str]) -> None:
        self.added = added
        self.updated = updated
        self.removed = removed

    @property
    def total_changes(self) -> int:
        return len(self.added) + len(self.updated) + len(self.removed)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"PatchResult(added={self.added}, updated={self.updated}, "
            f"removed={self.removed})"
        )


def _parse(text: str) -> Dict[str, str]:
    result: Dict[str, str] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" in stripped:
            key, _, value = stripped.partition("=")
            result[key.strip()] = value.strip()
    return result


def _unparse(data: Dict[str, str]) -> str:
    return "\n".join(f"{k}={v}" for k, v in sorted(data.items())) + "\n"


def patch_profile(
    store_dir: Path,
    profile: str,
    password: str,
    set_keys: Optional[Dict[str, str]] = None,
    remove_keys: Optional[list[str]] = None,
) -> PatchResult:
    """Load *profile*, apply key mutations, and save it back."""
    try:
        current_text = load_profile(store_dir, profile, password)
    except FileNotFoundError:
        raise ProfileNotFoundError(f"Profile '{profile}' does not exist.")

    data = _parse(current_text)
    set_keys = set_keys or {}
    remove_keys = remove_keys or []

    added: list[str] = []
    updated: list[str] = []
    removed: list[str] = []

    for key, value in set_keys.items():
        if key in data:
            if data[key] != value:
                updated.append(key)
        else:
            added.append(key)
        data[key] = value

    for key in remove_keys:
        if key in data:
            del data[key]
            removed.append(key)

    save_profile(store_dir, profile, _unparse(data), password)
    return PatchResult(added=added, updated=updated, removed=removed)
