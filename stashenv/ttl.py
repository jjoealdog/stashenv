"""Per-profile TTL (time-to-live) management for stashenv.

TTL is stored as a duration in seconds alongside a 'created_at' timestamp.
A profile is considered stale when now() > created_at + ttl_seconds.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Optional


class TTLExpiredError(Exception):
    """Raised when a profile's TTL has elapsed."""


class ProfileNotFoundError(Exception):
    """Raised when the target profile does not exist."""


def _ttl_path(store_dir: Path) -> Path:
    return store_dir / ".ttl.json"


def _load_ttl(store_dir: Path) -> dict:
    p = _ttl_path(store_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_ttl(store_dir: Path, data: dict) -> None:
    _ttl_path(store_dir).write_text(json.dumps(data, indent=2))


def set_ttl(store_dir: Path, profile: str, ttl_seconds: int) -> None:
    """Assign a TTL to *profile*, resetting its creation timestamp."""
    data = _load_ttl(store_dir)
    data[profile] = {"ttl": ttl_seconds, "created_at": time.time()}
    _save_ttl(store_dir, data)


def clear_ttl(store_dir: Path, profile: str) -> None:
    """Remove the TTL entry for *profile* if present."""
    data = _load_ttl(store_dir)
    data.pop(profile, None)
    _save_ttl(store_dir, data)


def get_ttl(store_dir: Path, profile: str) -> Optional[dict]:
    """Return the raw TTL record for *profile*, or None."""
    return _load_ttl(store_dir).get(profile)


def is_stale(store_dir: Path, profile: str) -> bool:
    """Return True when the profile's TTL has elapsed."""
    record = get_ttl(store_dir, profile)
    if record is None:
        return False
    elapsed = time.time() - record["created_at"]
    return elapsed > record["ttl"]


def check_ttl(store_dir: Path, profile: str) -> None:
    """Raise TTLExpiredError if the profile is stale."""
    if is_stale(store_dir, profile):
        raise TTLExpiredError(
            f"Profile '{profile}' has exceeded its TTL and is no longer valid."
        )


def list_ttl(store_dir: Path) -> list[dict]:
    """Return a list of dicts describing all TTL-tracked profiles."""
    data = _load_ttl(store_dir)
    rows = []
    for name, rec in data.items():
        elapsed = time.time() - rec["created_at"]
        remaining = max(0.0, rec["ttl"] - elapsed)
        rows.append(
            {
                "profile": name,
                "ttl": rec["ttl"],
                "remaining": remaining,
                "stale": elapsed > rec["ttl"],
            }
        )
    return rows
