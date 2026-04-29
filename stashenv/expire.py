"""Profile expiry — set a TTL on a profile so it auto-expires after a date."""

import json
from datetime import datetime, timezone
from pathlib import Path


class ProfileExpiredError(Exception):
    pass


class ProfileNotFoundError(Exception):
    pass


def _expiry_path(store_dir: Path) -> Path:
    return store_dir / ".expiry.json"


def _load_expiry(store_dir: Path) -> dict:
    path = _expiry_path(store_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_expiry(store_dir: Path, data: dict) -> None:
    _expiry_path(store_dir).write_text(json.dumps(data, indent=2))


def set_expiry(store_dir: Path, profile: str, expires_at: datetime) -> None:
    """Set an expiry datetime (UTC) for a profile."""
    data = _load_expiry(store_dir)
    data[profile] = expires_at.astimezone(timezone.utc).isoformat()
    _save_expiry(store_dir, data)


def clear_expiry(store_dir: Path, profile: str) -> bool:
    """Remove expiry for a profile. Returns True if one was removed."""
    data = _load_expiry(store_dir)
    if profile in data:
        del data[profile]
        _save_expiry(store_dir, data)
        return True
    return False


def get_expiry(store_dir: Path, profile: str) -> datetime | None:
    """Return the expiry datetime for a profile, or None if not set."""
    data = _load_expiry(store_dir)
    raw = data.get(profile)
    if raw is None:
        return None
    return datetime.fromisoformat(raw)


def check_expiry(store_dir: Path, profile: str) -> None:
    """Raise ProfileExpiredError if the profile has passed its expiry date."""
    expiry = get_expiry(store_dir, profile)
    if expiry is None:
        return
    now = datetime.now(timezone.utc)
    if now >= expiry:
        raise ProfileExpiredError(
            f"Profile '{profile}' expired at {expiry.isoformat()}"
        )


def list_expiry(store_dir: Path) -> dict[str, datetime]:
    """Return a mapping of profile -> expiry datetime for all profiles with TTLs."""
    data = _load_expiry(store_dir)
    return {name: datetime.fromisoformat(ts) for name, ts in data.items()}
