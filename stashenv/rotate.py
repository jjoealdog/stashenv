"""Password rotation for encrypted profiles."""

from pathlib import Path
from stashenv.store import _profile_path, list_profiles
from stashenv.crypto import encrypt, decrypt


class ProfileNotFoundError(Exception):
    pass


class RotationError(Exception):
    pass


def rotate_profile(profile: str, old_password: str, new_password: str, store_dir: Path) -> None:
    """Re-encrypt a single profile with a new password."""
    path = _profile_path(profile, store_dir)
    if not path.exists():
        raise ProfileNotFoundError(f"Profile '{profile}' not found")

    ciphertext = path.read_bytes()
    try:
        plaintext = decrypt(ciphertext, old_password)
    except Exception as exc:
        raise RotationError(f"Failed to decrypt profile '{profile}': wrong password?") from exc

    new_ciphertext = encrypt(plaintext, new_password)
    path.write_bytes(new_ciphertext)


def rotate_all_profiles(
    old_password: str, new_password: str, store_dir: Path
) -> tuple[list[str], list[str]]:
    """Re-encrypt all profiles with a new password.

    Returns (succeeded, failed) lists of profile names.
    """
    succeeded: list[str] = []
    failed: list[str] = []

    for profile in list_profiles(store_dir):
        try:
            rotate_profile(profile, old_password, new_password, store_dir)
            succeeded.append(profile)
        except (RotationError, Exception):
            failed.append(profile)

    return succeeded, failed
