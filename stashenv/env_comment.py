"""Add, remove, and list inline and block comments in a profile."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from stashenv.store import _profile_path, load_profile, save_profile


class ProfileNotFoundError(FileNotFoundError):
    pass


@dataclass
class CommentResult:
    profile: str
    changes: int
    lines: List[str] = field(default_factory=list)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<CommentResult profile={self.profile!r} changes={self.changes}>"


def _parse_lines(text: str) -> List[str]:
    return text.splitlines()


def _unparse_lines(lines: List[str]) -> str:
    return "\n".join(lines) + ("\n" if lines else "")


def set_block_comment(store_dir: Path, profile: str, key: str, comment: str, password: str) -> CommentResult:
    """Insert or replace a # comment line immediately above the given key."""
    path = _profile_path(store_dir, profile)
    if not path.exists():
        raise ProfileNotFoundError(profile)

    text = load_profile(store_dir, profile, password)
    lines = _parse_lines(text)
    new_lines: List[str] = []
    changes = 0
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if "=" in stripped and not stripped.startswith("#"):
            k = stripped.split("=", 1)[0].strip()
            if k == key:
                # Remove any existing comment line directly above
                if new_lines and new_lines[-1].strip().startswith("#"):
                    new_lines.pop()
                new_lines.append(f"# {comment}")
                changes += 1
        new_lines.append(line)
        i += 1

    save_profile(store_dir, profile, _unparse_lines(new_lines), password)
    return CommentResult(profile=profile, changes=changes, lines=new_lines)


def remove_block_comment(store_dir: Path, profile: str, key: str, password: str) -> CommentResult:
    """Remove the comment line immediately above the given key, if any."""
    path = _profile_path(store_dir, profile)
    if not path.exists():
        raise ProfileNotFoundError(profile)

    text = load_profile(store_dir, profile, password)
    lines = _parse_lines(text)
    new_lines: List[str] = []
    changes = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if "=" in stripped and not stripped.startswith("#"):
            k = stripped.split("=", 1)[0].strip()
            if k == key and new_lines and new_lines[-1].strip().startswith("#"):
                new_lines.pop()
                changes += 1
        new_lines.append(line)

    save_profile(store_dir, profile, _unparse_lines(new_lines), password)
    return CommentResult(profile=profile, changes=changes, lines=new_lines)


def list_comments(store_dir: Path, profile: str, password: str) -> List[dict]:
    """Return a list of {key, comment} dicts for all commented keys."""
    path = _profile_path(store_dir, profile)
    if not path.exists():
        raise ProfileNotFoundError(profile)

    text = load_profile(store_dir, profile, password)
    lines = _parse_lines(text)
    results = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        if "=" in stripped and not stripped.startswith("#") and i > 0:
            prev = lines[i - 1].strip()
            if prev.startswith("#"):
                k = stripped.split("=", 1)[0].strip()
                results.append({"key": k, "comment": prev.lstrip("# ").strip()})
    return results
