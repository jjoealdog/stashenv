"""Archive and restore profiles to/from a compressed tarball."""

from __future__ import annotations

import io
import json
import tarfile
from pathlib import Path

from stashenv.store import _store_dir, _profile_path, list_profiles


class ArchiveError(Exception):
    pass


class ProfileNotFoundError(ArchiveError):
    pass


def archive_profiles(
    store_dir: Path,
    dest: Path,
    profiles: list[str] | None = None,
) -> list[str]:
    """Write named profiles (or all profiles) into a .tar.gz archive.

    Returns the list of profile names that were archived.
    """
    available = list_profiles(store_dir)
    names = profiles if profiles is not None else available

    missing = [n for n in names if n not in available]
    if missing:
        raise ProfileNotFoundError(
            f"Profile(s) not found: {', '.join(missing)}"
        )

    meta = {"profiles": names}
    meta_bytes = json.dumps(meta).encode()

    with tarfile.open(dest, "w:gz") as tar:
        # Write manifest
        info = tarfile.TarInfo(name="manifest.json")
        info.size = len(meta_bytes)
        tar.addfile(info, io.BytesIO(meta_bytes))

        for name in names:
            path = _profile_path(store_dir, name)
            tar.add(path, arcname=f"profiles/{name}.env.enc")

    return names


def restore_profiles(
    store_dir: Path,
    src: Path,
    overwrite: bool = False,
) -> list[str]:
    """Restore profiles from an archive created by archive_profiles.

    Returns the list of profile names that were restored.
    """
    if not src.exists():
        raise ArchiveError(f"Archive not found: {src}")

    store_dir.mkdir(parents=True, exist_ok=True)
    restored: list[str] = []

    with tarfile.open(src, "r:gz") as tar:
        manifest_member = tar.getmember("manifest.json")
        f = tar.extractfile(manifest_member)
        meta = json.loads(f.read())
        names = meta["profiles"]

        for name in names:
            dest_path = _profile_path(store_dir, name)
            if dest_path.exists() and not overwrite:
                raise ArchiveError(
                    f"Profile '{name}' already exists. Use overwrite=True to replace."
                )
            member = tar.getmember(f"profiles/{name}.env.enc")
            data = tar.extractfile(member).read()
            dest_path.write_bytes(data)
            restored.append(name)

    return restored
