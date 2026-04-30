"""Profile inheritance — load a profile on top of a base profile."""
from __future__ import annotations

from pathlib import Path
from typing import Dict

from stashenv.store import load_profile, save_profile, list_profiles


class ProfileNotFoundError(Exception):
    pass


class CircularInheritanceError(Exception):
    pass


def _parse(text: str) -> Dict[str, str]:
    result: Dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        result[key.strip()] = value
    return result


def _unparse(data: Dict[str, str]) -> str:
    return "\n".join(f"{k}={v}" for k, v in data.items()) + "\n"


def resolve_profile(
    profile: str,
    password: str,
    base: str,
    base_password: str,
    store_dir: Path | None = None,
) -> str:
    """Return env text with *base* values merged under *profile*.

    Keys present in *profile* take precedence; missing keys are filled
    in from *base*.
    """
    if profile == base:
        raise CircularInheritanceError(
            f"Profile '{profile}' cannot inherit from itself."
        )

    profiles = list_profiles(store_dir=store_dir)
    if profile not in profiles:
        raise ProfileNotFoundError(f"Profile '{profile}' not found.")
    if base not in profiles:
        raise ProfileNotFoundError(f"Base profile '{base}' not found.")

    base_text = load_profile(base, base_password, store_dir=store_dir)
    profile_text = load_profile(profile, password, store_dir=store_dir)

    base_data = _parse(base_text)
    profile_data = _parse(profile_text)

    merged = {**base_data, **profile_data}
    return _unparse(merged)


def inherit_into_new(
    profile: str,
    password: str,
    base: str,
    base_password: str,
    destination: str,
    dest_password: str,
    store_dir: Path | None = None,
) -> None:
    """Merge *base* under *profile* and save result as *destination*."""
    merged_text = resolve_profile(
        profile, password, base, base_password, store_dir=store_dir
    )
    save_profile(destination, merged_text, dest_password, store_dir=store_dir)
