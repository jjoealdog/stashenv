"""Thin wrappers around store functions that emit audit events.

Import these instead of the bare store functions when you want automatic
audit logging on every profile operation.
"""

from pathlib import Path

from stashenv import store, audit
from stashenv.store import _store_dir


def save_profile(name: str, plaintext: str, password: str) -> None:
    """Save a profile and record the event in the audit log."""
    sd = _store_dir()
    try:
        store.save_profile(name, plaintext, password)
        audit.record_event(sd, "save", name, success=True)
    except Exception:
        audit.record_event(sd, "save", name, success=False)
        raise


def load_profile(name: str, password: str) -> str:
    """Load a profile and record the event in the audit log."""
    sd = _store_dir()
    try:
        result = store.load_profile(name, password)
        audit.record_event(sd, "load", name, success=True)
        return result
    except Exception:
        audit.record_event(sd, "load", name, success=False)
        raise


def delete_profile(name: str) -> None:
    """Delete a profile and record the event in the audit log."""
    sd = _store_dir()
    try:
        store.delete_profile(name)
        audit.record_event(sd, "delete", name, success=True)
    except Exception:
        audit.record_event(sd, "delete", name, success=False)
        raise
