"""Split a profile into multiple smaller profiles by key prefix or explicit grouping."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from stashenv.store import save_profile, load_profile


class ProfileNotFoundError(Exception):
    pass


class SplitError(Exception):
    pass


@dataclass
class SplitResult:
    source: str
    destinations: List[str] = field(default_factory=list)
    total_keys: int = 0
    keys_placed: int = 0

    @property
    def unplaced(self) -> int:
        return self.total_keys - self.keys_placed


def _parse(text: str) -> Dict[str, str]:
    result: Dict[str, str] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" in stripped:
            k, _, v = stripped.partition("=")
            result[k.strip()] = v.strip()
    return result


def _unparse(pairs: Dict[str, str]) -> str:
    return "\n".join(f"{k}={v}" for k, v in pairs.items()) + "\n"


def split_profile(
    store_dir: Path,
    source: str,
    password: str,
    groups: Dict[str, List[str]],
    *,
    remainder_profile: Optional[str] = None,
    overwrite: bool = False,
) -> SplitResult:
    """Split *source* into multiple profiles according to *groups*.

    *groups* maps destination profile name -> list of keys to include.
    Keys not covered by any group land in *remainder_profile* (if given).
    """
    try:
        plaintext = load_profile(store_dir, source, password)
    except FileNotFoundError:
        raise ProfileNotFoundError(f"Profile '{source}' not found.")

    all_keys = _parse(plaintext)
    result = SplitResult(source=source, total_keys=len(all_keys))
    placed_keys: set = set()

    for dest_name, keys in groups.items():
        dest_path = store_dir / f"{dest_name}.env.enc"
        if dest_path.exists() and not overwrite:
            raise SplitError(f"Destination profile '{dest_name}' already exists.")
        subset = {k: all_keys[k] for k in keys if k in all_keys}
        save_profile(store_dir, dest_name, _unparse(subset), password)
        placed_keys.update(subset.keys())
        result.destinations.append(dest_name)

    result.keys_placed = len(placed_keys)

    if remainder_profile:
        remainder = {k: v for k, v in all_keys.items() if k not in placed_keys}
        if remainder:
            dest_path = store_dir / f"{remainder_profile}.env.enc"
            if dest_path.exists() and not overwrite:
                raise SplitError(f"Remainder profile '{remainder_profile}' already exists.")
            save_profile(store_dir, remainder_profile, _unparse(remainder), password)
            result.destinations.append(remainder_profile)
            result.keys_placed += len(remainder)

    return result
