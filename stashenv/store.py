"""Profile store: save, load, list, and delete named .env profiles."""

import os
import json
from pathlib import Path
from typing import Optional

from stashenv.crypto import encrypt, decrypt

DEFAULT_STORE_DIR = Path.home() / ".stashenv"


def _store_dir(project_id: str, base: Optional[Path] = None) -> Path:
    """Return the directory where profiles for a project are stored."""
    root = base or DEFAULT_STORE_DIR
    return root / project_id


def _profile_path(project_id: str, profile_name: str, base: Optional[Path] = None) -> Path:
    return _store_dir(project_id, base) / f"{profile_name}.enc"


def save_profile(
    project_id: str,
    profile_name: str,
    env_content: str,
    password: str,
    base: Optional[Path] = None,
) -> Path:
    """Encrypt and save a named profile for the given project."""
    store = _store_dir(project_id, base)
    store.mkdir(parents=True, exist_ok=True)

    ciphertext = encrypt(env_content.encode(), password)
    path = _profile_path(project_id, profile_name, base)
    path.write_bytes(ciphertext)
    return path


def load_profile(
    project_id: str,
    profile_name: str,
    password: str,
    base: Optional[Path] = None,
) -> str:
    """Decrypt and return the env content for a named profile."""
    path = _profile_path(project_id, profile_name, base)
    if not path.exists():
        raise FileNotFoundError(f"Profile '{profile_name}' not found for project '{project_id}'")

    ciphertext = path.read_bytes()
    plaintext = decrypt(ciphertext, password)
    return plaintext.decode()


def list_profiles(project_id: str, base: Optional[Path] = None) -> list[str]:
    """Return a list of saved profile names for a project."""
    store = _store_dir(project_id, base)
    if not store.exists():
        return []
    return [p.stem for p in sorted(store.glob("*.enc"))]


def delete_profile(
    project_id: str,
    profile_name: str,
    base: Optional[Path] = None,
) -> bool:
    """Delete a named profile. Returns True if deleted, False if it didn't exist."""
    path = _profile_path(project_id, profile_name, base)
    if not path.exists():
        return False
    path.unlink()
    return True
