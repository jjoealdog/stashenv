"""Manage favorite (starred) profiles per project."""

import json
from pathlib import Path


class FavoriteNotFoundError(Exception):
    pass


def _favorites_path(store_dir: Path) -> Path:
    return store_dir / "favorites.json"


def _load_favorites(store_dir: Path) -> list[str]:
    path = _favorites_path(store_dir)
    if not path.exists():
        return []
    return json.loads(path.read_text())


def _save_favorites(store_dir: Path, favorites: list[str]) -> None:
    _favorites_path(store_dir).write_text(json.dumps(favorites, indent=2))


def add_favorite(store_dir: Path, profile: str) -> None:
    """Mark a profile as a favorite. No-op if already favorited."""
    favorites = _load_favorites(store_dir)
    if profile not in favorites:
        favorites.append(profile)
        _save_favorites(store_dir, favorites)


def remove_favorite(store_dir: Path, profile: str) -> None:
    """Remove a profile from favorites."""
    favorites = _load_favorites(store_dir)
    if profile not in favorites:
        raise FavoriteNotFoundError(f"Profile '{profile}' is not in favorites.")
    favorites.remove(profile)
    _save_favorites(store_dir, favorites)


def list_favorites(store_dir: Path) -> list[str]:
    """Return all favorited profile names."""
    return _load_favorites(store_dir)


def is_favorite(store_dir: Path, profile: str) -> bool:
    """Return True if the profile is marked as a favorite."""
    return profile in _load_favorites(store_dir)
