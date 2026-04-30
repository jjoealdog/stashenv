"""Tests for stashenv.clone."""

import pytest
from pathlib import Path
from stashenv.store import save_profile, load_profile
from stashenv.clone import (
    clone_profile,
    ProfileNotFoundError,
    DestinationExistsError,
    InvalidStoreError,
)


@pytest.fixture()
def stores(tmp_path: Path):
    src = tmp_path / "src_store"
    dst = tmp_path / "dst_store"
    src.mkdir()
    dst.mkdir()
    return src, dst


def test_clone_creates_file_in_destination(stores):
    src, dst = stores
    save_profile("prod", "KEY=val", "secret", store_dir=src)
    clone_profile("prod", src, dst)
    assert (dst / "prod.env.enc").exists()


def test_cloned_profile_loadable_with_same_password(stores):
    src, dst = stores
    save_profile("prod", "KEY=hello", "s3cr3t", store_dir=src)
    clone_profile("prod", src, dst)
    content = load_profile("prod", "s3cr3t", store_dir=dst)
    assert content == "KEY=hello"


def test_clone_with_different_dest_name(stores):
    src, dst = stores
    save_profile("dev", "X=1", "pw", store_dir=src)
    clone_profile("dev", src, dst, dest_name="staging")
    assert (dst / "staging.env.enc").exists()
    assert not (dst / "dev.env.enc").exists()


def test_clone_missing_source_raises(stores):
    src, dst = stores
    with pytest.raises(ProfileNotFoundError):
        clone_profile("ghost", src, dst)


def test_clone_existing_destination_raises_without_overwrite(stores):
    src, dst = stores
    save_profile("prod", "A=1", "pw", store_dir=src)
    save_profile("prod", "A=2", "pw", store_dir=dst)
    with pytest.raises(DestinationExistsError):
        clone_profile("prod", src, dst)


def test_clone_overwrite_flag_replaces_destination(stores):
    src, dst = stores
    save_profile("prod", "A=NEW", "pw", store_dir=src)
    save_profile("prod", "A=OLD", "pw", store_dir=dst)
    clone_profile("prod", src, dst, overwrite=True)
    content = load_profile("prod", "pw", store_dir=dst)
    assert content == "A=NEW"


def test_clone_invalid_dest_store_raises(stores, tmp_path):
    src, _ = stores
    save_profile("prod", "K=v", "pw", store_dir=src)
    with pytest.raises(InvalidStoreError):
        clone_profile("prod", src, tmp_path / "nonexistent")


def test_clone_empty_dest_name_raises(stores):
    src, dst = stores
    save_profile("prod", "K=v", "pw", store_dir=src)
    with pytest.raises(ValueError):
        clone_profile("prod", src, dst, dest_name="   ")
