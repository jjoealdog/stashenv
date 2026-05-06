"""Rename a key inside a stored .env profile without re-encrypting from scratch."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from stashenv.store import load_profile, save_profile


class ProfileNotFoundError(FileNotFoundError):
    pass


class KeyNotFoundError(KeyError):
    pass


class KeyAlreadyExistsError(KeyError):
    pass


@dataclass
class RenameKeyResult:
    profile: str
    old_key: str
    new_key: str
    old_value: str

    def __repr__(self) -> str:  # pragma: no cover
        return f"<RenameKeyResult {self.profile}: {self.old_key!r} -> {self.new_key!r}>"


def _parse(text: str) -> list[str]:
    """Return raw lines preserving comments and blanks."""
    return text.splitlines(keepends=True)


def rename_key(
    store_dir: Path,
    profile: str,
    password: str,
    old_key: str,
    new_key: str,
    *,
    overwrite: bool = False,
) -> RenameKeyResult:
    """Load *profile*, rename *old_key* to *new_key*, and re-save.

    Raises
    ------
    ProfileNotFoundError  – profile file does not exist.
    KeyNotFoundError      – *old_key* is not present in the profile.
    KeyAlreadyExistsError – *new_key* already exists and *overwrite* is False.
    """
    try:
        plaintext: str = load_profile(store_dir, profile, password)
    except FileNotFoundError as exc:
        raise ProfileNotFoundError(profile) from exc

    lines = _parse(plaintext)
    found_old = False
    new_key_exists = False
    result_lines: list[str] = []
    old_value = ""

    for line in lines:
        stripped = line.rstrip("\n")
        if "=" in stripped and not stripped.lstrip().startswith("#"):
            key, _, value = stripped.partition("=")
            key = key.strip()
            if key == old_key:
                found_old = True
                old_value = value
                result_lines.append(f"{new_key}={value}\n")
                continue
            if key == new_key:
                new_key_exists = True
        result_lines.append(line if line.endswith("\n") else line + "\n")

    if not found_old:
        raise KeyNotFoundError(old_key)
    if new_key_exists and not overwrite:
        raise KeyAlreadyExistsError(new_key)

    new_text = "".join(result_lines).rstrip("\n")
    save_profile(store_dir, profile, password, new_text)
    return RenameKeyResult(profile=profile, old_key=old_key, new_key=new_key, old_value=old_value)
