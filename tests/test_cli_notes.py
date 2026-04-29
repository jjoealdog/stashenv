import pytest
from click.testing import CliRunner
from pathlib import Path
from unittest.mock import patch
from stashenv.cli_notes import notes_group
from stashenv.notes import set_note


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def store(tmp_path):
    store_dir = tmp_path / ".stashenv"
    store_dir.mkdir(parents=True)
    # Create a dummy profile file so list_profiles returns it
    (store_dir / "prod.env.enc").write_bytes(b"dummy")
    return store_dir


def test_set_cmd_sets_note(runner, store):
    with patch("stashenv.cli_notes._store_dir", return_value=store), \
         patch("stashenv.cli_notes.list_profiles", return_value=["prod"]):
        result = runner.invoke(notes_group, ["set", "prod", "Production env"])
    assert result.exit_code == 0
    assert "Note set" in result.output


def test_set_cmd_missing_profile_exits_nonzero(runner, store):
    with patch("stashenv.cli_notes._store_dir", return_value=store), \
         patch("stashenv.cli_notes.list_profiles", return_value=[]):
        result = runner.invoke(notes_group, ["set", "ghost", "Some note"])
    assert result.exit_code != 0


def test_get_cmd_shows_note(runner, store):
    set_note("prod", "Hello note", store_dir=store)
    with patch("stashenv.cli_notes._store_dir", return_value=store):
        result = runner.invoke(notes_group, ["get", "prod"])
    assert result.exit_code == 0
    assert "Hello note" in result.output


def test_get_cmd_no_note_message(runner, store):
    with patch("stashenv.cli_notes._store_dir", return_value=store):
        result = runner.invoke(notes_group, ["get", "prod"])
    assert result.exit_code == 0
    assert "No note" in result.output


def test_remove_cmd_removes_existing_note(runner, store):
    set_note("prod", "To be removed", store_dir=store)
    with patch("stashenv.cli_notes._store_dir", return_value=store):
        result = runner.invoke(notes_group, ["remove", "prod"])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_remove_cmd_no_note_message(runner, store):
    with patch("stashenv.cli_notes._store_dir", return_value=store):
        result = runner.invoke(notes_group, ["remove", "ghost"])
    assert result.exit_code == 0
    assert "No note found" in result.output


def test_list_cmd_shows_all_notes(runner, store):
    set_note("prod", "Production", store_dir=store)
    set_note("dev", "Development", store_dir=store)
    with patch("stashenv.cli_notes._store_dir", return_value=store):
        result = runner.invoke(notes_group, ["list"])
    assert result.exit_code == 0
    assert "prod" in result.output
    assert "dev" in result.output


def test_list_cmd_empty_message(runner, store):
    with patch("stashenv.cli_notes._store_dir", return_value=store):
        result = runner.invoke(notes_group, ["list"])
    assert result.exit_code == 0
    assert "No notes" in result.output
