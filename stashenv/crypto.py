"""Encryption and decryption utilities for stashenv profiles."""

import os
import base64
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet, InvalidToken


SALT_SIZE = 16
ITERATIONS = 390000


def derive_key(password: str, salt: bytes) -> bytes:
    """Derive a Fernet-compatible key from a password and salt."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=ITERATIONS,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))


def encrypt(plaintext: str, password: str) -> bytes:
    """
    Encrypt plaintext using a password.

    Returns salt + encrypted data as raw bytes.
    """
    salt = os.urandom(SALT_SIZE)
    key = derive_key(password, salt)
    token = Fernet(key).encrypt(plaintext.encode())
    return salt + token


def decrypt(data: bytes, password: str) -> str:
    """
    Decrypt data using a password.

    Expects data in the format: salt + encrypted token.
    Raises ValueError on bad password or corrupted data.
    """
    salt = data[:SALT_SIZE]
    token = data[SALT_SIZE:]
    key = derive_key(password, salt)
    try:
        return Fernet(key).decrypt(token).decode()
    except InvalidToken:
        raise ValueError("Decryption failed: invalid password or corrupted data.")
