"""Tests for stashenv.export — profile export/import functionality."""

import json
import base64
import pytest
from pathlib import Path
from unittest.mock import patch

from stashenv.export import export_profile, import_profile, export_all_profiles
from stashenv.store import save_profile, load_profile


PASSWORD = "hunter2"
PROJECT = "myapp"
PROFILE = "staging"
ENV_CONTENT = b"DB_URL=postgres://localhost/test\nDEBUG=true\n"


@pytest.fixture()
def populated_store(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHENV_DIR", str(tmp_path / "store"))
    save_profile(PROJECT, PROFILE, ENV_CONTENT, PASSWORD)
    return tmp_path


def test_export_creates_bundle_file(populated_store, tmp_path):
    out = export_profile(PROJECT, PROFILE, tmp_path / "bundles")
    assert out.exists()
    assert out.suffix == ".stashenv"
    assert f"{PROJECT}__{PROFILE}" in out.name


def test_export_bundle_is_valid_json(populated_store, tmp_path):
    out = export_profile(PROJECT, PROFILE, tmp_path / "bundles")
    data = json.loads(out.read_text())
    assert data["project"] == PROJECT
    assert data["profile"] == PROFILE
    assert "data" in data


def test_export_bundle_data_is_base64(populated_store, tmp_path):
    out = export_profile(PROJECT, PROFILE, tmp_path / "bundles")
    data = json.loads(out.read_text())
    decoded = base64.b64decode(data["data"])
    assert isinstance(decoded, bytes)
    assert len(decoded) > 0


def test_export_missing_profile_raises(populated_store, tmp_path):
    with pytest.raises(FileNotFoundError):
        export_profile(PROJECT, "nonexistent", tmp_path / "bundles")


def test_import_roundtrip(populated_store, tmp_path, monkeypatch):
    bundle_dir = tmp_path / "bundles"
    out = export_profile(PROJECT, PROFILE, bundle_dir)

    # Import into a fresh store directory
    fresh_store = tmp_path / "fresh_store"
    monkeypatch.setenv("STASHENV_DIR", str(fresh_store))

    project, profile = import_profile(out)
    assert project == PROJECT
    assert profile == PROFILE

    recovered = load_profile(project, profile, PASSWORD)
    assert recovered == ENV_CONTENT


def test_import_with_dest_project_override(populated_store, tmp_path, monkeypatch):
    bundle_dir = tmp_path / "bundles"
    out = export_profile(PROJECT, PROFILE, bundle_dir)

    fresh_store = tmp_path / "fresh2"
    monkeypatch.setenv("STASHENV_DIR", str(fresh_store))

    project, profile = import_profile(out, dest_project="otherapp")
    assert project == "otherapp"


def test_import_missing_bundle_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        import_profile(tmp_path / "ghost.stashenv")


def test_export_all_profiles(populated_store, tmp_path, monkeypatch):
    monkeypatch.setenv("STASHENV_DIR", str(populated_store / "store"))
    save_profile(PROJECT, "production", b"ENV=prod\n", PASSWORD)
    paths = export_all_profiles(PROJECT, tmp_path / "bundles")
    assert len(paths) == 2
    assert all(p.exists() for p in paths)


def test_export_all_no_profiles_raises(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHENV_DIR", str(tmp_path / "empty_store"))
    with pytest.raises(ValueError):
        export_all_profiles("ghostproject", tmp_path / "bundles")
