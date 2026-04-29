"""Compare a profile's current state against a historical snapshot."""

from pathlib import Path
from typing import List

from stashenv.diff import DiffEntry, parse_env_text, diff_profiles, format_diff
from stashenv.history import list_snapshots, get_snapshot
from stashenv.store import load_profile


class SnapshotNotFoundError(Exception):
    pass


class ProfileNotFoundError(Exception):
    pass


def diff_against_snapshot(
    store_dir: Path,
    profile: str,
    password: str,
    version: int,
    show_values: bool = False,
) -> List[DiffEntry]:
    """Return diff entries between a snapshot version and the current profile."""
    snapshots = list_snapshots(store_dir, profile)
    matching = [s for s in snapshots if s["version"] == version]
    if not matching:
        raise SnapshotNotFoundError(
            f"No snapshot v{version} found for profile '{profile}'"
        )

    snapshot_bytes = get_snapshot(store_dir, profile, version, password)
    snapshot_text = snapshot_bytes.decode()

    try:
        current_text = load_profile(store_dir, profile, password)
    except FileNotFoundError:
        raise ProfileNotFoundError(f"Profile '{profile}' not found")

    old_vars = parse_env_text(snapshot_text)
    new_vars = parse_env_text(current_text)

    return diff_profiles(old_vars, new_vars)


def format_snapshot_diff(
    entries: List[DiffEntry],
    profile: str,
    version: int,
    show_values: bool = False,
) -> str:
    """Format snapshot diff with a descriptive header."""
    header = f"--- {profile} @ v{version}\n+++ {profile} (current)\n"
    body = format_diff(entries, show_values=show_values)
    if not body.strip():
        return header + "(no differences)"
    return header + body
