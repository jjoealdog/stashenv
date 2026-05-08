"""Tests for stashenv.env_dedupe."""
from pathlib import Path

import pytest

from stashenv.env_dedupe import (
    DedupeResult,
    ProfileNotFoundError,
    dedupe_env_text,
    dedupe_profile,
)
from stashenv.store import save_profile


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def store(tmp_path: Path) -> Path:
    return tmp_path / "store"


# ---------------------------------------------------------------------------
# dedupe_env_text
# ---------------------------------------------------------------------------


def test_no_duplicates_returns_unchanged():
    text = "FOO=1\nBAR=2\nBAZ=3\n"
    result = dedupe_env_text(text)
    assert result.total_removed == 0
    assert result.kept_text == text


def test_detects_single_duplicate_key():
    text = "FOO=1\nFOO=2\n"
    result = dedupe_env_text(text)
    assert "FOO" in result.removed
    assert result.total_removed == 1


def test_keep_last_retains_final_occurrence():
    text = "FOO=first\nBAR=x\nFOO=last\n"
    result = dedupe_env_text(text, keep="last")
    assert "FOO=last\n" in result.kept_text
    assert "FOO=first" not in result.kept_text


def test_keep_first_retains_initial_occurrence():
    text = "FOO=first\nBAR=x\nFOO=last\n"
    result = dedupe_env_text(text, keep="first")
    assert "FOO=first\n" in result.kept_text
    assert "FOO=last" not in result.kept_text


def test_comments_and_blank_lines_preserved():
    text = "# comment\n\nFOO=1\nFOO=2\n"
    result = dedupe_env_text(text, keep="first")
    assert "# comment\n" in result.kept_text
    assert "\n" in result.kept_text


def test_multiple_duplicate_keys_all_reported():
    text = "A=1\nB=2\nA=3\nB=4\n"
    result = dedupe_env_text(text)
    assert set(result.removed) == {"A", "B"}


def test_invalid_keep_raises_value_error():
    with pytest.raises(ValueError, match="keep must be"):
        dedupe_env_text("FOO=1\n", keep="middle")


def test_returns_dedupe_result_instance():
    result = dedupe_env_text("X=1\n")
    assert isinstance(result, DedupeResult)


# ---------------------------------------------------------------------------
# dedupe_profile
# ---------------------------------------------------------------------------


def test_dedupe_profile_saves_cleaned_text(store: Path):
    text = "KEY=old\nKEY=new\n"
    save_profile("dev", text, "pw", store)
    result = dedupe_profile("dev", "pw", store, keep="last")
    assert result.total_removed == 1
    assert result.profile == "dev"


def test_dedupe_profile_no_change_does_not_corrupt(store: Path):
    text = "A=1\nB=2\n"
    save_profile("clean", text, "pw", store)
    result = dedupe_profile("clean", "pw", store)
    assert result.total_removed == 0


def test_dedupe_profile_missing_raises(store: Path):
    with pytest.raises(ProfileNotFoundError):
        dedupe_profile("ghost", "pw", store)


def test_dedupe_profile_result_profile_name_set(store: Path):
    save_profile("staging", "X=1\nX=2\n", "pw", store)
    result = dedupe_profile("staging", "pw", store)
    assert result.profile == "staging"
