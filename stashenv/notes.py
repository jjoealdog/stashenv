"""Per-profile notes/annotations stored alongside encrypted profiles."""

import json
from pathlib import Path
from stashenv.store import _store_dir


def _notes_path(store_dir: Path) -> Path:
    return store_dir / "notes.json"


def _load_notes(store_dir: Path) -> dict:
    path = _notes_path(store_dir)
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)


def _save_notes(store_dir: Path, notes: dict) -> None:
    path = _notes_path(store_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(notes, f, indent=2)


def set_note(profile: str, text: str, store_dir: Path | None = None) -> None:
    """Set or replace the note for a profile."""
    store_dir = store_dir or _store_dir()
    notes = _load_notes(store_dir)
    notes[profile] = text
    _save_notes(store_dir, notes)


def get_note(profile: str, store_dir: Path | None = None) -> str | None:
    """Return the note for a profile, or None if not set."""
    store_dir = store_dir or _store_dir()
    notes = _load_notes(store_dir)
    return notes.get(profile)


def remove_note(profile: str, store_dir: Path | None = None) -> bool:
    """Remove the note for a profile. Returns True if a note existed."""
    store_dir = store_dir or _store_dir()
    notes = _load_notes(store_dir)
    if profile not in notes:
        return False
    del notes[profile]
    _save_notes(store_dir, notes)
    return True


def list_notes(store_dir: Path | None = None) -> dict:
    """Return a dict of all profile -> note mappings."""
    store_dir = store_dir or _store_dir()
    return _load_notes(store_dir)
