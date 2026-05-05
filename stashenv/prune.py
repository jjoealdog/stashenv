"""Prune stale profiles based on age, expiry, or explicit criteria."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from stashenv.store import _store_dir, list_profiles, delete_profile
from stashenv.expire import get_expiry


class PruneResult:
    def __init__(self, pruned: List[str], skipped: List[str], errors: List[str]):
        self.pruned = pruned
        self.skipped = skipped
        self.errors = errors

    @property
    def total(self) -> int:
        return len(self.pruned)


def _profile_mtime(store_dir: Path, name: str) -> Optional[datetime]:
    """Return last-modified time of a profile file as UTC datetime."""
    from stashenv.store import _profile_path
    p = _profile_path(store_dir, name)
    try:
        ts = p.stat().st_mtime
        return datetime.fromtimestamp(ts, tz=timezone.utc)
    except FileNotFoundError:
        return None


def prune_expired(store_dir: Optional[Path] = None) -> PruneResult:
    """Delete all profiles whose expiry date has passed."""
    store_dir = store_dir or _store_dir()
    pruned, skipped, errors = [], [], []
    now = datetime.now(tz=timezone.utc)

    for name in list_profiles(store_dir):
        expiry = get_expiry(store_dir, name)
        if expiry is None:
            skipped.append(name)
            continue
        if expiry <= now:
            try:
                delete_profile(store_dir, name)
                pruned.append(name)
            except Exception as exc:  # pragma: no cover
                errors.append(f"{name}: {exc}")
        else:
            skipped.append(name)

    return PruneResult(pruned=pruned, skipped=skipped, errors=errors)


def prune_older_than(days: int, store_dir: Optional[Path] = None) -> PruneResult:
    """Delete profiles whose file mtime is older than *days* days."""
    from datetime import timedelta
    store_dir = store_dir or _store_dir()
    pruned, skipped, errors = [], [], []
    cutoff = datetime.now(tz=timezone.utc) - timedelta(days=days)

    for name in list_profiles(store_dir):
        mtime = _profile_mtime(store_dir, name)
        if mtime is None:
            skipped.append(name)
            continue
        if mtime < cutoff:
            try:
                delete_profile(store_dir, name)
                pruned.append(name)
            except Exception as exc:  # pragma: no cover
                errors.append(f"{name}: {exc}")
        else:
            skipped.append(name)

    return PruneResult(pruned=pruned, skipped=skipped, errors=errors)
