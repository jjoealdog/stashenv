"""Promote a profile from one environment tier to another (e.g. dev -> staging -> prod)."""

from pathlib import Path
from typing import List

from stashenv.copy import copy_profile, ProfileAlreadyExistsError, ProfileNotFoundError

DEFAULT_TIERS: List[str] = ["dev", "staging", "prod"]


class TierError(Exception):
    """Raised when a tier-related operation fails."""


def _tier_of(profile: str, tiers: List[str]) -> str | None:
    """Return the tier suffix found in the profile name, or None."""
    for tier in tiers:
        if profile == tier or profile.endswith(f".{tier}"):
            return tier
    return None


def _next_tier(current: str, tiers: List[str]) -> str:
    """Return the tier that follows *current* in the tier list."""
    try:
        idx = tiers.index(current)
    except ValueError:
        raise TierError(f"Tier '{current}' is not in the tier list: {tiers}")
    if idx + 1 >= len(tiers):
        raise TierError(f"'{current}' is already the last tier; cannot promote further.")
    return tiers[idx + 1]


def _build_destination(source: str, current_tier: str, next_tier: str) -> str:
    """Derive the destination profile name by replacing the tier suffix."""
    if source == current_tier:
        return next_tier
    prefix = source[: -(len(current_tier))].rstrip(".")
    return f"{prefix}.{next_tier}"


def promote_profile(
    store_dir: Path,
    source: str,
    password: str,
    *,
    tiers: List[str] = DEFAULT_TIERS,
    overwrite: bool = False,
    destination: str | None = None,
) -> str:
    """Copy *source* to the next environment tier and return the destination name.

    Parameters
    ----------
    store_dir:   Root store directory (passed through to copy_profile).
    source:      Name of the profile to promote.
    password:    Encryption password (same password is used for the copy).
    tiers:       Ordered list of tier names to use when auto-detecting the next tier.
    overwrite:   When True, overwrite an existing destination profile.
    destination: Explicit destination name; skips auto-detection when provided.
    """
    if destination is None:
        current_tier = _tier_of(source, tiers)
        if current_tier is None:
            raise TierError(
                f"Cannot auto-detect tier for '{source}'. "
                f"Profile name must end with one of: {tiers}"
            )
        next_t = _next_tier(current_tier, tiers)
        destination = _build_destination(source, current_tier, next_t)

    copy_profile(store_dir, source, destination, password, overwrite=overwrite)
    return destination
