"""Flatten multiple profiles into a single merged .env text.

Later profiles take precedence over earlier ones (last-wins strategy).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Tuple

from stashenv.store import load_profile


class ProfileNotFoundError(KeyError):
    pass


@dataclass
class FlattenResult:
    text: str
    key_sources: Dict[str, str] = field(default_factory=dict)  # key -> profile name
    profiles_used: List[str] = field(default_factory=list)

    @property
    def total_keys(self) -> int:
        return len(self.key_sources)

    def __repr__(self) -> str:  # pragma: no cover
        return f"FlattenResult(profiles={self.profiles_used}, keys={self.total_keys})"


def _parse(text: str) -> List[Tuple[str, str, str]]:
    """Return list of (key, value, raw_line) for non-comment, non-blank lines."""
    entries = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        entries.append((key.strip(), value.strip(), line))
    return entries


def flatten_profiles(
    store_dir: str,
    profile_names: List[str],
    password: str,
) -> FlattenResult:
    """Load each profile in order and merge, last-wins on duplicate keys."""
    merged: Dict[str, Tuple[str, str]] = {}  # key -> (value, source_profile)

    for name in profile_names:
        try:
            text = load_profile(store_dir, name, password)
        except FileNotFoundError:
            raise ProfileNotFoundError(name)

        for key, value, _raw in _parse(text):
            merged[key] = (value, name)

    lines = [f"{k}={v}" for k, (v, _src) in merged.items()]
    flat_text = "\n".join(lines) + ("\n" if lines else "")
    key_sources = {k: src for k, (_v, src) in merged.items()}

    return FlattenResult(
        text=flat_text,
        key_sources=key_sources,
        profiles_used=list(profile_names),
    )
