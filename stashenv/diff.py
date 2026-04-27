"""Diff utilities for comparing .env profiles."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass
class DiffEntry:
    key: str
    status: str  # 'added', 'removed', 'changed', 'unchanged'
    left_value: Optional[str] = None
    right_value: Optional[str] = None


def parse_env_text(text: str) -> Dict[str, str]:
    """Parse a .env-style text into a dict, ignoring comments and blanks."""
    result: Dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        result[key.strip()] = value.strip()
    return result


def diff_profiles(
    left_text: str,
    right_text: str,
    show_values: bool = False,
) -> List[DiffEntry]:
    """Return a list of DiffEntry comparing two env profile texts."""
    left = parse_env_text(left_text)
    right = parse_env_text(right_text)
    all_keys = sorted(set(left) | set(right))

    entries: List[DiffEntry] = []
    for key in all_keys:
        if key in left and key not in right:
            entries.append(DiffEntry(
                key=key,
                status="removed",
                left_value=left[key] if show_values else None,
            ))
        elif key not in left and key in right:
            entries.append(DiffEntry(
                key=key,
                status="added",
                right_value=right[key] if show_values else None,
            ))
        elif left[key] != right[key]:
            entries.append(DiffEntry(
                key=key,
                status="changed",
                left_value=left[key] if show_values else None,
                right_value=right[key] if show_values else None,
            ))
        else:
            entries.append(DiffEntry(
                key=key,
                status="unchanged",
            ))
    return entries


def format_diff(entries: List[DiffEntry], show_values: bool = False) -> str:
    """Render diff entries as a human-readable string."""
    symbols = {"added": "+", "removed": "-", "changed": "~", "unchanged": " "}
    lines = []
    for e in entries:
        sym = symbols[e.status]
        if show_values and e.status == "changed":
            lines.append(f"{sym} {e.key}={e.left_value!r} -> {e.right_value!r}")
        elif show_values and e.status == "added":
            lines.append(f"{sym} {e.key}={e.right_value!r}")
        elif show_values and e.status == "removed":
            lines.append(f"{sym} {e.key}={e.left_value!r}")
        else:
            lines.append(f"{sym} {e.key}")
    return "\n".join(lines)
