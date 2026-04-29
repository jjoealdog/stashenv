"""Merge two profiles into a new profile."""
from __future__ import annotations

from pathlib import Path
from typing import Literal

from stashenv.store import _profile_path, load_profile, save_profile, list_profiles


class ProfileNotFoundError(Exception):
    pass


class ProfileAlreadyExistsError(Exception):
    pass


MergeStrategy = Literal["base", "override", "union"]


def merge_profiles(
    store_dir: Path,
    base_name: str,
    override_name: str,
    dest_name: str,
    base_password: str,
    override_password: str,
    dest_password: str,
    strategy: MergeStrategy = "override",
    overwrite: bool = False,
) -> int:
    """Merge two profiles into *dest_name*.

    Strategies
    ----------
    base     – keep base value on conflict
    override – keep override value on conflict (default)
    union    – include all keys from both; conflicts use override value

    Returns the number of keys written to the destination profile.
    """
    existing = list_profiles(store_dir)

    if base_name not in existing:
        raise ProfileNotFoundError(f"Profile '{base_name}' not found")
    if override_name not in existing:
        raise ProfileNotFoundError(f"Profile '{override_name}' not found")
    if dest_name in existing and not overwrite:
        raise ProfileAlreadyExistsError(
            f"Profile '{dest_name}' already exists. Use overwrite=True to replace it."
        )

    base_text = load_profile(store_dir, base_name, base_password)
    override_text = load_profile(store_dir, override_name, override_password)

    base_vars = _parse(base_text)
    override_vars = _parse(override_text)

    if strategy == "base":
        merged = {**override_vars, **base_vars}
    elif strategy == "override":
        merged = {**base_vars, **override_vars}
    else:  # union – same as override for conflicts
        merged = {**base_vars, **override_vars}

    dest_text = "\n".join(f"{k}={v}" for k, v in merged.items())
    save_profile(store_dir, dest_name, dest_text, dest_password)
    return len(merged)


def _parse(env_text: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in env_text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, _, value = line.partition("=")
            result[key.strip()] = value
    return result
