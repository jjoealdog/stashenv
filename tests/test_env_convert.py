"""Tests for stashenv.env_convert."""

from __future__ import annotations

import json
import pytest
from pathlib import Path

from stashenv.env_convert import (
    export_as,
    import_from,
    UnsupportedFormatError,
)
from stashenv.store import save_profile, load_profile


@pytest.fixture()
def store(tmp_path: Path):
    store_dir = tmp_path / "store"
    store_dir.mkdir()
    env_text = "DB_HOST=localhost\nDB_PORT=5432\nSECRET=abc123\n"
    save_profile(store_dir, "dev", "pass", env_text)
    return store_dir


def test_export_dotenv_returns_key_value_pairs(store):
    out = export_as(store, "dev", "pass", "dotenv")
    assert "DB_HOST=localhost" in out
    assert "DB_PORT=5432" in out


def test_export_json_is_valid_json(store):
    out = export_as(store, "dev", "pass", "json")
    data = json.loads(out)
    assert data["DB_HOST"] == "localhost"
    assert data["DB_PORT"] == "5432"


def test_export_yaml_contains_key_colon_value(store):
    out = export_as(store, "dev", "pass", "yaml")
    assert "DB_HOST: localhost" in out
    assert "DB_PORT: 5432" in out


def test_export_unsupported_format_raises(store):
    with pytest.raises(UnsupportedFormatError):
        export_as(store, "dev", "pass", "toml")


def test_import_dotenv_saves_profile(store):
    text = "NEW_KEY=hello\nOTHER=world\n"
    import_from(store, "imported", "pass2", text, "dotenv")
    raw = load_profile(store, "imported", "pass2")
    assert "NEW_KEY=hello" in raw


def test_import_json_saves_profile(store):
    data = {"FOO": "bar", "BAZ": "qux"}
    text = json.dumps(data)
    import_from(store, "from_json", "pass3", text, "json")
    raw = load_profile(store, "from_json", "pass3")
    assert "FOO=bar" in raw
    assert "BAZ=qux" in raw


def test_import_yaml_saves_profile(store):
    text = "ALPHA: one\nBETA: two\n"
    import_from(store, "from_yaml", "pass4", text, "yaml")
    raw = load_profile(store, "from_yaml", "pass4")
    assert "ALPHA=one" in raw
    assert "BETA=two" in raw


def test_import_unsupported_format_raises(store):
    with pytest.raises(UnsupportedFormatError):
        import_from(store, "x", "p", "data", "xml")


def test_import_json_non_dict_raises(store):
    with pytest.raises(ValueError):
        import_from(store, "x", "p", json.dumps([1, 2, 3]), "json")


def test_roundtrip_json(store):
    exported = export_as(store, "dev", "pass", "json")
    import_from(store, "roundtrip", "newpass", exported, "json")
    raw = load_profile(store, "roundtrip", "newpass")
    assert "DB_HOST=localhost" in raw
