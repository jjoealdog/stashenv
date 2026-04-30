"""Clone a profile to a different store directory."""

from pathlib import Path
from stashenv.store import _profile_path, list_profiles


class ProfileNotFoundError(FileNotFoundError):
    pass


class DestinationExistsError(FileExistsError):
    pass


class InvalidStoreError(ValueError):
    pass


def clone_profile(
    name: str,
    source_store: Path,
    dest_store: Path,
    dest_name: str | None = None,
    overwrite: bool = False,
) -> Path:
    """Copy an encrypted profile blob from one store directory to another.

    Parameters
    ----------
    name:         profile name in the source store
    source_store: root directory of the source store
    dest_store:   root directory of the destination store
    dest_name:    name to use in the destination store (defaults to *name*)
    overwrite:    if True, replace an existing profile in the destination

    Returns the path of the newly written file.
    """
    if dest_name is None:
        dest_name = name

    if not dest_name.strip():
        raise ValueError("Destination profile name must not be empty.")

    src_path = _profile_path(name, store_dir=source_store)
    if not src_path.exists():
        raise ProfileNotFoundError(f"Profile '{name}' not found in {source_store}.")

    dest_store = Path(dest_store)
    if not dest_store.exists():
        raise InvalidStoreError(f"Destination store directory does not exist: {dest_store}")

    dst_path = _profile_path(dest_name, store_dir=dest_store)
    if dst_path.exists() and not overwrite:
        raise DestinationExistsError(
            f"Profile '{dest_name}' already exists in {dest_store}. "
            "Use overwrite=True to replace it."
        )

    dst_path.write_bytes(src_path.read_bytes())
    return dst_path
