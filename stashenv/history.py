"""Profile version history — snapshot profiles on save and restore previous versions."""

import json
import time
from pathlib import Path
from typing import List, Optional


def _history_dir(store_dir: Path, profile: str) -> Path:
    d = store_dir / ".history" / profile
    d.mkdir(parents=True, exist_ok=True)
    return d


def _history_index_path(store_dir: Path, profile: str) -> Path:
    return _history_dir(store_dir, profile) / "index.json"


def _load_index(store_dir: Path, profile: str) -> List[dict]:
    path = _history_index_path(store_dir, profile)
    if not path.exists():
        return []
    return json.loads(path.read_text())


def _save_index(store_dir: Path, profile: str, index: List[dict]) -> None:
    _history_index_path(store_dir, profile).write_text(json.dumps(index, indent=2))


def snapshot_profile(store_dir: Path, profile: str, encrypted_data: bytes, note: str = "") -> int:
    """Save a snapshot of the encrypted profile blob. Returns the new version number."""
    index = _load_index(store_dir, profile)
    version = len(index) + 1
    ts = time.time()
    snap_path = _history_dir(store_dir, profile) / f"v{version}.bin"
    snap_path.write_bytes(encrypted_data)
    index.append({"version": version, "timestamp": ts, "note": note, "file": snap_path.name})
    _save_index(store_dir, profile, index)
    return version


def list_snapshots(store_dir: Path, profile: str) -> List[dict]:
    """Return snapshot metadata list, newest first."""
    return list(reversed(_load_index(store_dir, profile)))


def get_snapshot(store_dir: Path, profile: str, version: int) -> Optional[bytes]:
    """Return raw encrypted bytes for a given version, or None if not found."""
    index = _load_index(store_dir, profile)
    for entry in index:
        if entry["version"] == version:
            snap_path = _history_dir(store_dir, profile) / entry["file"]
            if snap_path.exists():
                return snap_path.read_bytes()
    return None


def clear_history(store_dir: Path, profile: str) -> int:
    """Delete all snapshots for a profile. Returns number of snapshots removed."""
    index = _load_index(store_dir, profile)
    hdir = _history_dir(store_dir, profile)
    for entry in index:
        snap = hdir / entry["file"]
        if snap.exists():
            snap.unlink()
    index_path = _history_index_path(store_dir, profile)
    if index_path.exists():
        index_path.unlink()
    return len(index)
