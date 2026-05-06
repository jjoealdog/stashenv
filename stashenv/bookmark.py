"""Named bookmarks that point to a profile + store directory pair."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional


class BookmarkNotFoundError(KeyError):
    pass


class BookmarkAlreadyExistsError(KeyError):
    pass


def _bookmark_path(store_dir: Path) -> Path:
    return store_dir / ".bookmarks.json"


def _load_bookmarks(store_dir: Path) -> Dict[str, str]:
    p = _bookmark_path(store_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_bookmarks(store_dir: Path, data: Dict[str, str]) -> None:
    _bookmark_path(store_dir).write_text(json.dumps(data, indent=2))


def add_bookmark(
    store_dir: Path,
    name: str,
    profile: str,
    *,
    overwrite: bool = False,
) -> None:
    """Associate *name* with *profile* in *store_dir*."""
    if not name:
        raise ValueError("Bookmark name must not be empty.")
    data = _load_bookmarks(store_dir)
    if name in data and not overwrite:
        raise BookmarkAlreadyExistsError(name)
    data[name] = profile
    _save_bookmarks(store_dir, data)


def remove_bookmark(store_dir: Path, name: str) -> None:
    data = _load_bookmarks(store_dir)
    if name not in data:
        raise BookmarkNotFoundError(name)
    del data[name]
    _save_bookmarks(store_dir, data)


def resolve_bookmark(store_dir: Path, name: str) -> str:
    """Return the profile name that *name* points to."""
    data = _load_bookmarks(store_dir)
    if name not in data:
        raise BookmarkNotFoundError(name)
    return data[name]


def list_bookmarks(store_dir: Path) -> Dict[str, str]:
    """Return all bookmarks as {name: profile}."""
    return dict(_load_bookmarks(store_dir))
