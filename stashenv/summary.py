"""Generate a human-readable summary of a profile's metadata."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from stashenv.store import _profile_path, list_profiles
from stashenv.tags import get_tags
from stashenv.notes import get_note
from stashenv.lock import is_locked
from stashenv.expire import get_expiry
from stashenv.favorite import list_favorites
from stashenv.alias import list_aliases


@dataclass
class ProfileSummary:
    name: str
    size_bytes: int
    tags: list[str] = field(default_factory=list)
    note: Optional[str] = None
    locked: bool = False
    expires_at: Optional[str] = None
    is_favorite: bool = False
    aliases: list[str] = field(default_factory=list)


def summarise_profile(store_dir: Path, name: str) -> ProfileSummary:
    """Collect metadata for *name* from the given store directory."""
    path = _profile_path(store_dir, name)
    if not path.exists():
        raise FileNotFoundError(f"Profile '{name}' not found in {store_dir}")

    size = path.stat().st_size
    tags = get_tags(store_dir, name)
    note = get_note(store_dir, name)
    locked = is_locked(store_dir, name)

    expiry = get_expiry(store_dir, name)
    expires_at = expiry.isoformat() if expiry is not None else None

    favorites = list_favorites(store_dir)
    is_fav = name in favorites

    all_aliases = list_aliases(store_dir)
    profile_aliases = [alias for alias, target in all_aliases.items() if target == name]

    return ProfileSummary(
        name=name,
        size_bytes=size,
        tags=tags,
        note=note,
        locked=locked,
        expires_at=expires_at,
        is_favorite=is_fav,
        aliases=profile_aliases,
    )


def format_summary(summary: ProfileSummary) -> str:
    """Return a formatted, human-readable string for *summary*."""
    lines: list[str] = [
        f"Profile : {summary.name}",
        f"Size    : {summary.size_bytes} bytes",
        f"Locked  : {'yes' if summary.locked else 'no'}",
        f"Favorite: {'yes' if summary.is_favorite else 'no'}",
        f"Tags    : {', '.join(summary.tags) if summary.tags else '(none)'}",
        f"Aliases : {', '.join(summary.aliases) if summary.aliases else '(none)'}",
        f"Expires : {summary.expires_at if summary.expires_at else '(never)'}",
        f"Note    : {summary.note if summary.note else '(none)'}",
    ]
    return "\n".join(lines)
