"""Search profiles for keys or values matching a regex pattern."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from stashenv.store import load_profile, list_profiles


@dataclass
class GrepMatch:
    profile: str
    key: str
    value: str
    matched_on: str  # 'key', 'value', or 'both'

    def __repr__(self) -> str:  # pragma: no cover
        return f"GrepMatch(profile={self.profile!r}, key={self.key!r}, matched_on={self.matched_on!r})"


def _parse(text: str) -> dict[str, str]:
    result = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        k, _, v = line.partition("=")
        result[k.strip()] = v.strip()
    return result


def grep_profiles(
    pattern: str,
    password: str,
    store_dir: Path,
    *,
    search_keys: bool = True,
    search_values: bool = True,
    case_sensitive: bool = False,
    profiles: Optional[List[str]] = None,
) -> List[GrepMatch]:
    """Return all key/value pairs across profiles whose key or value matches *pattern*."""
    flags = 0 if case_sensitive else re.IGNORECASE
    try:
        rx = re.compile(pattern, flags)
    except re.error as exc:
        raise ValueError(f"Invalid regex pattern: {exc}") from exc

    target_profiles = profiles if profiles is not None else list_profiles(store_dir)
    matches: List[GrepMatch] = []

    for name in target_profiles:
        try:
            text = load_profile(name, password, store_dir)
        except Exception:
            continue
        for key, value in _parse(text).items():
            key_hit = search_keys and bool(rx.search(key))
            val_hit = search_values and bool(rx.search(value))
            if key_hit or val_hit:
                if key_hit and val_hit:
                    matched_on = "both"
                elif key_hit:
                    matched_on = "key"
                else:
                    matched_on = "value"
                matches.append(GrepMatch(profile=name, key=key, value=value, matched_on=matched_on))

    return matches


def format_grep_results(matches: List[GrepMatch], *, show_values: bool = False) -> str:
    if not matches:
        return "No matches found."
    lines = []
    for m in matches:
        if show_values:
            lines.append(f"[{m.profile}]  {m.key}={m.value}  ({m.matched_on})")
        else:
            lines.append(f"[{m.profile}]  {m.key}  ({m.matched_on})")
    return "\n".join(lines)
