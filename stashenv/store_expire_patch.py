"""Patch store functions to enforce expiry checks on load.

Call apply_patch() once at startup to wrap load_profile so that
attempting to load an expired profile raises ProfileExpiredError.
"""

import stashenv.store as _store
from stashenv.expire import check_expiry
from stashenv.expire import ProfileExpiredError  # re-export for convenience

_original_load = _store.load_profile


def load_profile(profile: str, password: str) -> str:
    """Load a profile, raising ProfileExpiredError if it has expired."""
    store_dir = _store._store_dir()
    check_expiry(store_dir, profile)
    return _original_load(profile, password)


def apply_patch() -> None:
    """Replace store.load_profile with the expiry-aware version."""
    _store.load_profile = load_profile


__all__ = ["load_profile", "apply_patch", "ProfileExpiredError"]
