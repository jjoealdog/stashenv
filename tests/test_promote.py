"""Tests for stashenv.promote."""

import pytest
from pathlib import Path

from stashenv.store import save_profile, load_profile
from stashenv.promote import (
    promote_profile,
    TierError,
    _tier_of,
    _next_tier,
    _build_destination,
    DEFAULT_TIERS,
)


@pytest.fixture()
def store(tmp_path: Path) -> Path:
    return tmp_path


ENV_TEXT = b"DB_HOST=localhost\nDB_PORT=5432\n"
PASSWORD = "secret"


def _save(store_dir: Path, name: str) -> None:
    save_profile(store_dir, name, ENV_TEXT, PASSWORD)


# ---------------------------------------------------------------------------
# Unit tests for helpers
# ---------------------------------------------------------------------------

def test_tier_of_detects_suffix():
    assert _tier_of("myapp.dev", DEFAULT_TIERS) == "dev"
    assert _tier_of("myapp.staging", DEFAULT_TIERS) == "staging"
    assert _tier_of("myapp.prod", DEFAULT_TIERS) == "prod"


def test_tier_of_bare_name():
    assert _tier_of("dev", DEFAULT_TIERS) == "dev"


def test_tier_of_returns_none_for_unknown():
    assert _tier_of("myapp.qa", DEFAULT_TIERS) is None


def test_next_tier_advances_correctly():
    assert _next_tier("dev", DEFAULT_TIERS) == "staging"
    assert _next_tier("staging", DEFAULT_TIERS) == "prod"


def test_next_tier_raises_at_last_tier():
    with pytest.raises(TierError, match="last tier"):
        _next_tier("prod", DEFAULT_TIERS)


def test_build_destination_replaces_suffix():
    assert _build_destination("myapp.dev", "dev", "staging") == "myapp.staging"
    assert _build_destination("dev", "dev", "staging") == "staging"


# ---------------------------------------------------------------------------
# Integration tests
# ---------------------------------------------------------------------------

def test_promote_profile_creates_destination(store: Path):
    _save(store, "myapp.dev")
    dest = promote_profile(store, "myapp.dev", PASSWORD)
    assert dest == "myapp.staging"
    assert (store / "myapp.staging.env").exists()


def test_promote_profile_content_matches(store: Path):
    _save(store, "myapp.dev")
    promote_profile(store, "myapp.dev", PASSWORD)
    assert load_profile(store, "myapp.staging", PASSWORD) == ENV_TEXT


def test_promote_profile_original_still_exists(store: Path):
    _save(store, "myapp.dev")
    promote_profile(store, "myapp.dev", PASSWORD)
    assert load_profile(store, "myapp.dev", PASSWORD) == ENV_TEXT


def test_promote_profile_staging_to_prod(store: Path):
    _save(store, "myapp.staging")
    dest = promote_profile(store, "myapp.staging", PASSWORD)
    assert dest == "myapp.prod"


def test_promote_profile_explicit_destination(store: Path):
    _save(store, "myapp.dev")
    dest = promote_profile(store, "myapp.dev", PASSWORD, destination="custom.prod")
    assert dest == "custom.prod"
    assert (store / "custom.prod.env").exists()


def test_promote_profile_unknown_tier_raises(store: Path):
    _save(store, "myapp.qa")
    with pytest.raises(TierError, match="auto-detect"):
        promote_profile(store, "myapp.qa", PASSWORD)


def test_promote_profile_already_at_last_tier_raises(store: Path):
    _save(store, "myapp.prod")
    with pytest.raises(TierError, match="last tier"):
        promote_profile(store, "myapp.prod", PASSWORD)
