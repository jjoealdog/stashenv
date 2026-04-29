"""Profile alias management — map short names to profile names."""

from __future__ import annotations

import json
from pathlib import Path


class AliasNotFoundError(Exception):
    pass


class AliasAlreadyExistsError(Exception):
    pass


def _alias_path(store_dir: Path) -> Path:
    return store_dir / ".aliases.json"


def _load_aliases(store_dir: Path) -> dict[str, str]:
    path = _alias_path(store_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_aliases(store_dir: Path, aliases: dict[str, str]) -> None:
    _alias_path(store_dir).write_text(json.dumps(aliases, indent=2))


def set_alias(store_dir: Path, alias: str, profile: str, overwrite: bool = False) -> None:
    """Create or update an alias pointing to a profile."""
    if not alias or not alias.strip():
        raise ValueError("Alias name must not be empty")
    aliases = _load_aliases(store_dir)
    if alias in aliases and not overwrite:
        raise AliasAlreadyExistsError(f"Alias '{alias}' already exists (points to '{aliases[alias]}')")
    aliases[alias] = profile
    _save_aliases(store_dir, aliases)


def remove_alias(store_dir: Path, alias: str) -> None:
    """Remove an existing alias."""
    aliases = _load_aliases(store_dir)
    if alias not in aliases:
        raise AliasNotFoundError(f"Alias '{alias}' not found")
    del aliases[alias]
    _save_aliases(store_dir, aliases)


def resolve_alias(store_dir: Path, alias: str) -> str:
    """Return the profile name for the given alias."""
    aliases = _load_aliases(store_dir)
    if alias not in aliases:
        raise AliasNotFoundError(f"Alias '{alias}' not found")
    return aliases[alias]


def list_aliases(store_dir: Path) -> dict[str, str]:
    """Return all alias -> profile mappings."""
    return _load_aliases(store_dir)
