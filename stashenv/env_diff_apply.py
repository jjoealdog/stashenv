"""Apply a diff patch to an existing profile.

Takes the output of diff_profiles and applies add/remove/change
operations to a named profile in-place.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from stashenv.diff import DiffEntry, diff_profiles, parse_env_text
from stashenv.store import _profile_path, load_profile, save_profile


class ProfileNotFoundError(FileNotFoundError):
    """Raised when the target profile does not exist."""


class ConflictError(ValueError):
    """Raised when a patch operation cannot be applied cleanly."""


@dataclass
class ApplyResult:
    """Summary of a patch application."""

    profile: str
    added: List[str] = field(default_factory=list)
    removed: List[str] = field(default_factory=list)
    changed: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)

    @property
    def total_changes(self) -> int:
        return len(self.added) + len(self.removed) + len(self.changed)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"ApplyResult(profile={self.profile!r}, added={len(self.added)}, "
            f"removed={len(self.removed)}, changed={len(self.changed)}, "
            f"skipped={len(self.skipped)})"
        )


def apply_diff(
    profile: str,
    password: str,
    entries: List[DiffEntry],
    *,
    store_dir: Optional[Path] = None,
    skip_conflicts: bool = False,
) -> ApplyResult:
    """Apply a list of DiffEntry operations to *profile*.

    Parameters
    ----------
    profile:
        Name of the profile to patch.
    password:
        Decryption / re-encryption password for the profile.
    entries:
        List of :class:`~stashenv.diff.DiffEntry` objects describing the
        operations to apply.  Only entries whose ``status`` is ``'added'``,
        ``'removed'``, or ``'changed'`` are acted upon; ``'same'`` entries
        are silently ignored.
    store_dir:
        Override the default store directory (useful in tests).
    skip_conflicts:
        When *True*, keys that cannot be patched cleanly (e.g. a ``removed``
        entry for a key that is already absent) are added to
        ``ApplyResult.skipped`` instead of raising :class:`ConflictError`.

    Returns
    -------
    ApplyResult
    """
    path = _profile_path(profile, store_dir=store_dir)
    if not path.exists():
        raise ProfileNotFoundError(f"Profile not found: {profile!r}")

    raw_text = load_profile(profile, password, store_dir=store_dir)
    env: dict[str, str] = parse_env_text(raw_text)

    result = ApplyResult(profile=profile)

    for entry in entries:
        if entry.status == "same":
            continue

        key = entry.key

        if entry.status == "added":
            # Add a key that should not already exist.
            if key in env:
                if skip_conflicts:
                    result.skipped.append(key)
                    continue
                raise ConflictError(
                    f"Cannot add key {key!r}: already present in profile."
                )
            env[key] = entry.new_value or ""
            result.added.append(key)

        elif entry.status == "removed":
            # Remove a key that should currently exist.
            if key not in env:
                if skip_conflicts:
                    result.skipped.append(key)
                    continue
                raise ConflictError(
                    f"Cannot remove key {key!r}: not present in profile."
                )
            del env[key]
            result.removed.append(key)

        elif entry.status == "changed":
            # Update a key that should already exist.
            if key not in env:
                if skip_conflicts:
                    result.skipped.append(key)
                    continue
                raise ConflictError(
                    f"Cannot change key {key!r}: not present in profile."
                )
            env[key] = entry.new_value or ""
            result.changed.append(key)

    # Serialise the updated env dict back to .env text and re-save.
    new_text = "\n".join(f"{k}={v}" for k, v in env.items())
    save_profile(profile, new_text, password, store_dir=store_dir)

    return result
