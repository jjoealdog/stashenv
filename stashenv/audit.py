"""Audit log for profile access events."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path


AUDIT_FILENAME = ".audit.log"


def _audit_path(store_dir: Path) -> Path:
    return store_dir / AUDIT_FILENAME


def record_event(store_dir: Path, action: str, profile: str, success: bool = True) -> None:
    """Append a single audit event to the log file."""
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "profile": profile,
        "success": success,
        "pid": os.getpid(),
    }
    audit_file = _audit_path(store_dir)
    audit_file.parent.mkdir(parents=True, exist_ok=True)
    with audit_file.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")


def read_events(store_dir: Path) -> list[dict]:
    """Return all audit events as a list of dicts, oldest first."""
    audit_file = _audit_path(store_dir)
    if not audit_file.exists():
        return []
    events = []
    with audit_file.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                events.append(json.loads(line))
    return events


def clear_log(store_dir: Path) -> None:
    """Delete the audit log file."""
    audit_file = _audit_path(store_dir)
    if audit_file.exists():
        audit_file.unlink()
