"""Profile copy/clone functionality for stashenv."""

from pathlib import Path
from stashenv.store import _profile_path, list_profiles


class ProfileNotFoundError(Exception):
    pass


class ProfileAlreadyExistsError(Exception):
    pass


def copy_profile(store_dir: Path, source: str, destination: str) -> None:
    """Copy an encrypted profile file to a new name.

    The copied profile retains the same encryption, so the same
    password used to encrypt the source will be required to load
    the destination profile.

    Args:
        store_dir: Path to the stashenv store directory.
        source: Name of the existing profile to copy.
        destination: Name for the new profile copy.

    Raises:
        ValueError: If source or destination name is empty.
        ProfileNotFoundError: If the source profile does not exist.
        ProfileAlreadyExistsError: If the destination profile already exists.
    """
    if not source or not source.strip():
        raise ValueError("Source profile name must not be empty.")
    if not destination or not destination.strip():
        raise ValueError("Destination profile name must not be empty.")

    src_path = _profile_path(store_dir, source)
    dst_path = _profile_path(store_dir, destination)

    if not src_path.exists():
        raise ProfileNotFoundError(f"Profile '{source}' not found.")
    if dst_path.exists():
        raise ProfileAlreadyExistsError(f"Profile '{destination}' already exists.")

    dst_path.write_bytes(src_path.read_bytes())
