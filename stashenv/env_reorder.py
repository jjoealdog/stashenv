"""Reorder keys in an env profile to match a specified key order."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class ReorderResult:
    profile: str
    original_order: List[str]
    new_order: List[str]
    changed: bool

    @property
    def moved(self) -> int:
        return sum(1 for a, b in zip(self.original_order, self.new_order) if a != b)


def _parse_lines(text: str):
    """Return list of (key_or_none, raw_line) tuples."""
    result = []
    for line in text.splitlines(keepends=True):
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and "=" in stripped:
            key = stripped.split("=", 1)[0].strip()
            result.append((key, line))
        else:
            result.append((None, line))
    return result


def reorder_env_text(text: str, key_order: List[str], keep_unspecified: bool = True) -> str:
    """Reorder env text so that keys appear in *key_order* first.

    Keys not listed in *key_order* are appended at the end when
    *keep_unspecified* is True (default), otherwise they are dropped.
    Comments and blank lines that immediately precede a key travel with it.
    """
    parsed = _parse_lines(text)

    # Group each key line with any leading comment/blank lines
    blocks: dict[str, list[str]] = {}
    pending: list[str] = []
    key_sequence: list[str] = []

    for key, raw in parsed:
        if key is None:
            pending.append(raw)
        else:
            blocks[key] = pending + [raw]
            pending = []
            if key not in key_sequence:
                key_sequence.append(key)

    trailing = pending  # trailing comments/blanks after last key

    ordered_keys: list[str] = []
    for k in key_order:
        if k in blocks:
            ordered_keys.append(k)

    if keep_unspecified:
        for k in key_sequence:
            if k not in ordered_keys:
                ordered_keys.append(k)

    lines: list[str] = []
    for k in ordered_keys:
        lines.extend(blocks[k])
    lines.extend(trailing)

    return "".join(lines)


def reorder_profile(
    store_dir: Path,
    profile: str,
    password: str,
    key_order: List[str],
    keep_unspecified: bool = True,
) -> ReorderResult:
    """Load *profile* from *store_dir*, reorder its keys, and save it back."""
    from stashenv.store import load_profile, save_profile

    text = load_profile(store_dir, profile, password)
    parsed = _parse_lines(text)
    original_order = [k for k, _ in parsed if k is not None]

    new_text = reorder_env_text(text, key_order, keep_unspecified=keep_unspecified)

    new_parsed = _parse_lines(new_text)
    new_order = [k for k, _ in new_parsed if k is not None]

    changed = original_order != new_order
    if changed:
        save_profile(store_dir, profile, password, new_text)

    return ReorderResult(
        profile=profile,
        original_order=original_order,
        new_order=new_order,
        changed=changed,
    )
