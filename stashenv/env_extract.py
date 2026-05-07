"""Extract a subset of keys from a profile into a new profile."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from stashenv.store import load_profile, save_profile


class ProfileNotFoundError(Exception):
    pass


class NoKeysMatchedError(Exception):
    pass


@dataclass
class ExtractResult:
    source: str
    destination: str
    extracted_keys: List[str] = field(default_factory=list)
    skipped_keys: List[str] = field(default_factory=list)

    @property
    def total_extracted(self) -> int:
        return len(self.extracted_keys)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"ExtractResult(source={self.source!r}, destination={self.destination!r}, "
            f"extracted={self.total_extracted})"
        )


def _parse(text: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" in stripped:
            k, _, v = stripped.partition("=")
            result[k.strip()] = v.strip()
    return result


def _unparse(pairs: dict[str, str]) -> str:
    return "\n".join(f"{k}={v}" for k, v in pairs.items()) + "\n" if pairs else ""


def extract_profile(
    source: str,
    destination: str,
    keys: List[str],
    password: str,
    store_dir: Optional[Path] = None,
    *,
    strict: bool = False,
) -> ExtractResult:
    """Extract *keys* from *source* and save them as *destination*.

    If *strict* is True, raise NoKeysMatchedError when none of the
    requested keys exist in the source profile.
    """
    try:
        plaintext = load_profile(source, password, store_dir=store_dir)
    except FileNotFoundError:
        raise ProfileNotFoundError(f"Profile {source!r} not found")

    parsed = _parse(plaintext)
    result = ExtractResult(source=source, destination=destination)

    subset: dict[str, str] = {}
    for key in keys:
        if key in parsed:
            subset[key] = parsed[key]
            result.extracted_keys.append(key)
        else:
            result.skipped_keys.append(key)

    if strict and not result.extracted_keys:
        raise NoKeysMatchedError(
            f"None of the requested keys exist in profile {source!r}"
        )

    new_text = _unparse(subset)
    save_profile(destination, new_text, password, store_dir=store_dir)
    return result
