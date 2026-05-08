"""Detect and remove duplicate keys from a profile's env text."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from stashenv.store import load_profile, save_profile


class ProfileNotFoundError(FileNotFoundError):
    pass


@dataclass
class DedupeResult:
    profile: str
    removed: list[str] = field(default_factory=list)
    kept_text: str = ""

    @property
    def total_removed(self) -> int:
        return len(self.removed)

    def __repr__(self) -> str:  # pragma: no cover
        return f"DedupeResult(profile={self.profile!r}, removed={self.removed})"


def _parse(text: str) -> list[tuple[str, str]]:
    """Return list of (raw_line, key_or_empty) for every line."""
    lines = []
    for line in text.splitlines(keepends=True):
        stripped = line.strip()
        if stripped.startswith("#") or "=" not in stripped or not stripped:
            lines.append((line, ""))
        else:
            key = stripped.split("=", 1)[0].strip()
            lines.append((line, key))
    return lines


def dedupe_env_text(text: str, keep: str = "last") -> DedupeResult:
    """Remove duplicate keys from *text*, keeping either the 'first' or 'last' occurrence.

    Returns a DedupeResult with the cleaned text and the list of removed keys.
    """
    if keep not in ("first", "last"):
        raise ValueError("keep must be 'first' or 'last'")

    parsed = _parse(text)
    key_positions: dict[str, list[int]] = {}
    for idx, (_, key) in enumerate(parsed):
        if key:
            key_positions.setdefault(key, []).append(idx)

    removed_keys: list[str] = []
    drop_indices: set[int] = set()
    for key, positions in key_positions.items():
        if len(positions) > 1:
            removed_keys.append(key)
            to_drop = positions[1:] if keep == "first" else positions[:-1]
            drop_indices.update(to_drop)

    kept_lines = [line for idx, (line, _) in enumerate(parsed) if idx not in drop_indices]
    return DedupeResult(
        profile="",
        removed=removed_keys,
        kept_text="".join(kept_lines),
    )


def dedupe_profile(
    profile: str,
    password: str,
    store_dir: Path,
    keep: str = "last",
) -> DedupeResult:
    """Load *profile*, deduplicate its keys in-place, and save it back."""
    try:
        text = load_profile(profile, password, store_dir)
    except FileNotFoundError:
        raise ProfileNotFoundError(f"Profile not found: {profile}")

    result = dedupe_env_text(text, keep=keep)
    result.profile = profile

    if result.total_removed > 0:
        save_profile(profile, result.kept_text, password, store_dir)

    return result
