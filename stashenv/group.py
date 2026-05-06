"""Profile grouping — assign profiles to named groups and query by group."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List


class GroupNotFoundError(Exception):
    pass


class ProfileNotInGroupError(Exception):
    pass


def _groups_path(store_dir: Path) -> Path:
    return store_dir / ".groups.json"


def _load_groups(store_dir: Path) -> Dict[str, List[str]]:
    path = _groups_path(store_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_groups(store_dir: Path, data: Dict[str, List[str]]) -> None:
    _groups_path(store_dir).write_text(json.dumps(data, indent=2))


def add_to_group(store_dir: Path, group: str, profile: str) -> None:
    """Add *profile* to *group*, creating the group if needed."""
    data = _load_groups(store_dir)
    members = data.setdefault(group, [])
    if profile not in members:
        members.append(profile)
    _save_groups(store_dir, data)


def remove_from_group(store_dir: Path, group: str, profile: str) -> None:
    """Remove *profile* from *group*."""
    data = _load_groups(store_dir)
    if group not in data:
        raise GroupNotFoundError(group)
    if profile not in data[group]:
        raise ProfileNotInGroupError(profile)
    data[group].remove(profile)
    if not data[group]:
        del data[group]
    _save_groups(store_dir, data)


def list_groups(store_dir: Path) -> List[str]:
    """Return all group names."""
    return sorted(_load_groups(store_dir).keys())


def get_group_members(store_dir: Path, group: str) -> List[str]:
    """Return profiles belonging to *group*."""
    data = _load_groups(store_dir)
    if group not in data:
        raise GroupNotFoundError(group)
    return list(data[group])


def get_profile_groups(store_dir: Path, profile: str) -> List[str]:
    """Return all groups that contain *profile*."""
    data = _load_groups(store_dir)
    return sorted(g for g, members in data.items() if profile in members)


def delete_group(store_dir: Path, group: str) -> None:
    """Delete an entire group."""
    data = _load_groups(store_dir)
    if group not in data:
        raise GroupNotFoundError(group)
    del data[group]
    _save_groups(store_dir, data)


def rename_group(store_dir: Path, old_name: str, new_name: str) -> None:
    """Rename a group from *old_name* to *new_name*.

    Raises GroupNotFoundError if *old_name* does not exist.
    Raises ValueError if *new_name* already exists.
    """
    data = _load_groups(store_dir)
    if old_name not in data:
        raise GroupNotFoundError(old_name)
    if new_name in data:
        raise ValueError(f"Group '{new_name}' already exists")
    data[new_name] = data.pop(old_name)
    _save_groups(store_dir, data)
