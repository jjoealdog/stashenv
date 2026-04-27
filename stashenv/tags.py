"""Tag management for stashenv profiles."""

import json
from pathlib import Path
from typing import List, Dict

from stashenv.store import _store_dir


def _tags_path(store_dir: Path) -> Path:
    return store_dir / "tags.json"


def _load_tags(store_dir: Path) -> Dict[str, List[str]]:
    """Load the tags mapping from disk. Returns {profile: [tag, ...]}."""
    path = _tags_path(store_dir)
    if not path.exists():
        return {}
    with path.open("r") as f:
        return json.load(f)


def _save_tags(store_dir: Path, tags: Dict[str, List[str]]) -> None:
    path = _tags_path(store_dir)
    with path.open("w") as f:
        json.dump(tags, f, indent=2)


def add_tag(profile: str, tag: str, store_dir: Path = None) -> None:
    """Add a tag to a profile."""
    store_dir = store_dir or _store_dir()
    tags = _load_tags(store_dir)
    profile_tags = tags.get(profile, [])
    if tag not in profile_tags:
        profile_tags.append(tag)
    tags[profile] = profile_tags
    _save_tags(store_dir, tags)


def remove_tag(profile: str, tag: str, store_dir: Path = None) -> None:
    """Remove a tag from a profile. Silently ignores missing tags."""
    store_dir = store_dir or _store_dir()
    tags = _load_tags(store_dir)
    profile_tags = tags.get(profile, [])
    tags[profile] = [t for t in profile_tags if t != tag]
    _save_tags(store_dir, tags)


def get_tags(profile: str, store_dir: Path = None) -> List[str]:
    """Return list of tags for a profile."""
    store_dir = store_dir or _store_dir()
    tags = _load_tags(store_dir)
    return tags.get(profile, [])


def profiles_by_tag(tag: str, store_dir: Path = None) -> List[str]:
    """Return all profiles that have the given tag."""
    store_dir = store_dir or _store_dir()
    tags = _load_tags(store_dir)
    return [profile for profile, ptags in tags.items() if tag in ptags]


def delete_profile_tags(profile: str, store_dir: Path = None) -> None:
    """Remove all tag entries for a deleted profile."""
    store_dir = store_dir or _store_dir()
    tags = _load_tags(store_dir)
    tags.pop(profile, None)
    _save_tags(store_dir, tags)
