import pytest
from pathlib import Path
from stashenv.notes import set_note, get_note, remove_note, list_notes


@pytest.fixture
def store_dir(tmp_path):
    return tmp_path / ".stashenv"


def test_get_note_returns_none_when_no_notes_file(store_dir):
    result = get_note("prod", store_dir=store_dir)
    assert result is None


def test_set_note_creates_notes_file(store_dir):
    set_note("prod", "Production environment", store_dir=store_dir)
    notes_file = store_dir / "notes.json"
    assert notes_file.exists()


def test_set_note_stores_text(store_dir):
    set_note("prod", "Production environment", store_dir=store_dir)
    result = get_note("prod", store_dir=store_dir)
    assert result == "Production environment"


def test_set_note_overwrites_existing(store_dir):
    set_note("prod", "First note", store_dir=store_dir)
    set_note("prod", "Updated note", store_dir=store_dir)
    result = get_note("prod", store_dir=store_dir)
    assert result == "Updated note"


def test_multiple_profiles_have_independent_notes(store_dir):
    set_note("prod", "Production", store_dir=store_dir)
    set_note("dev", "Development", store_dir=store_dir)
    assert get_note("prod", store_dir=store_dir) == "Production"
    assert get_note("dev", store_dir=store_dir) == "Development"


def test_remove_note_returns_true_when_exists(store_dir):
    set_note("prod", "Some note", store_dir=store_dir)
    result = remove_note("prod", store_dir=store_dir)
    assert result is True


def test_remove_note_deletes_note(store_dir):
    set_note("prod", "Some note", store_dir=store_dir)
    remove_note("prod", store_dir=store_dir)
    assert get_note("prod", store_dir=store_dir) is None


def test_remove_note_returns_false_when_not_exists(store_dir):
    result = remove_note("ghost", store_dir=store_dir)
    assert result is False


def test_list_notes_empty_when_no_file(store_dir):
    result = list_notes(store_dir=store_dir)
    assert result == {}


def test_list_notes_returns_all_entries(store_dir):
    set_note("prod", "Production", store_dir=store_dir)
    set_note("staging", "Staging env", store_dir=store_dir)
    result = list_notes(store_dir=store_dir)
    assert result == {"prod": "Production", "staging": "Staging env"}
