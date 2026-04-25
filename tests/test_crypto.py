"""Tests for stashenv.crypto encryption/decryption utilities."""

import pytest
from stashenv.crypto import encrypt, decrypt, SALT_SIZE


SAMPLE_PLAINTEXT = "DATABASE_URL=postgres://localhost/mydb\nSECRET_KEY=supersecret\n"
PASSWORD = "hunter2"
WRONG_PASSWORD = "wrong_password"


def test_encrypt_returns_bytes():
    result = encrypt(SAMPLE_PLAINTEXT, PASSWORD)
    assert isinstance(result, bytes)


def test_encrypted_output_longer_than_salt():
    result = encrypt(SAMPLE_PLAINTEXT, PASSWORD)
    assert len(result) > SALT_SIZE


def test_decrypt_roundtrip():
    encrypted = encrypt(SAMPLE_PLAINTEXT, PASSWORD)
    decrypted = decrypt(encrypted, PASSWORD)
    assert decrypted == SAMPLE_PLAINTEXT


def test_decrypt_wrong_password_raises():
    encrypted = encrypt(SAMPLE_PLAINTEXT, PASSWORD)
    with pytest.raises(ValueError, match="Decryption failed"):
        decrypt(encrypted, WRONG_PASSWORD)


def test_encrypt_same_plaintext_produces_different_ciphertext():
    """Each encryption should use a fresh random salt."""
    enc1 = encrypt(SAMPLE_PLAINTEXT, PASSWORD)
    enc2 = encrypt(SAMPLE_PLAINTEXT, PASSWORD)
    assert enc1 != enc2


def test_decrypt_corrupted_data_raises():
    encrypted = encrypt(SAMPLE_PLAINTEXT, PASSWORD)
    corrupted = encrypted[:SALT_SIZE] + b"\x00" * (len(encrypted) - SALT_SIZE)
    with pytest.raises(ValueError):
        decrypt(corrupted, PASSWORD)


def test_empty_string_roundtrip():
    encrypted = encrypt("", PASSWORD)
    assert decrypt(encrypted, PASSWORD) == ""
