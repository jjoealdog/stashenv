"""Tests for stashenv.env_comment."""

import pytest
from pathlib import Path

from stashenv.store import save_profile
from stashenv.env_comment import (
    set_block_comment,
    remove_block_comment,
    list_comments,
    ProfileNotFoundError,
)

PASSWORD = "hunter2"


@pytest.fixture()
def store(tmp_path: Path):
    save_profile(tmp_path, "dev", "DB_HOST=localhost\nDB_PORT=5432\nSECRET=abc\n", PASSWORD)
    return tmp_path


def test_set_block_comment_inserts_comment(store):
    result = set_block_comment(store, "dev", "DB_HOST", "Primary database host", PASSWORD)
    assert result.changes == 1
    text = "\n".join(result.lines)
    assert "# Primary database host" in text
    idx = result.lines.index("# Primary database host")
    assert result.lines[idx + 1].startswith("DB_HOST=")


def test_set_block_comment_replaces_existing_comment(store):
    set_block_comment(store, "dev", "DB_HOST", "Old comment", PASSWORD)
    result = set_block_comment(store, "dev", "DB_HOST", "New comment", PASSWORD)
    text = "\n".join(result.lines)
    assert "# New comment" in text
    assert "# Old comment" not in text


def test_set_block_comment_only_targets_correct_key(store):
    result = set_block_comment(store, "dev", "DB_PORT", "Port number", PASSWORD)
    text = "\n".join(result.lines)
    assert "# Port number" in text
    idx = result.lines.index("# Port number")
    assert result.lines[idx + 1].startswith("DB_PORT=")


def test_set_block_comment_missing_profile_raises(store):
    with pytest.raises(ProfileNotFoundError):
        set_block_comment(store, "nope", "KEY", "comment", PASSWORD)


def test_remove_block_comment_removes_comment(store):
    set_block_comment(store, "dev", "DB_HOST", "Some comment", PASSWORD)
    result = remove_block_comment(store, "dev", "DB_HOST", PASSWORD)
    assert result.changes == 1
    text = "\n".join(result.lines)
    assert "# Some comment" not in text
    assert "DB_HOST=" in text


def test_remove_block_comment_no_comment_is_noop(store):
    result = remove_block_comment(store, "dev", "DB_HOST", PASSWORD)
    assert result.changes == 0


def test_remove_block_comment_missing_profile_raises(store):
    with pytest.raises(ProfileNotFoundError):
        remove_block_comment(store, "nope", "KEY", PASSWORD)


def test_list_comments_empty_when_no_comments(store):
    comments = list_comments(store, "dev", PASSWORD)
    assert comments == []


def test_list_comments_returns_commented_keys(store):
    set_block_comment(store, "dev", "DB_HOST", "Host setting", PASSWORD)
    set_block_comment(store, "dev", "SECRET", "Keep this safe", PASSWORD)
    comments = list_comments(store, "dev", PASSWORD)
    keys = [c["key"] for c in comments]
    assert "DB_HOST" in keys
    assert "SECRET" in keys


def test_list_comments_correct_text(store):
    set_block_comment(store, "dev", "DB_PORT", "TCP port", PASSWORD)
    comments = list_comments(store, "dev", PASSWORD)
    match = next(c for c in comments if c["key"] == "DB_PORT")
    assert match["comment"] == "TCP port"


def test_list_comments_missing_profile_raises(store):
    with pytest.raises(ProfileNotFoundError):
        list_comments(store, "ghost", PASSWORD)
