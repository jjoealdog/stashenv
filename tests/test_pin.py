"""Tests for stashenv/pin.py"""

import pytest
from pathlib import Path
from stashenv.pin import pin_profile, unpin_profile, get_pinned_profile, _PIN_FILENAME


@pytest.fixture
def project_dir(tmp_path):
    return tmp_path


def test_pin_profile_creates_file(project_dir):
    pin_profile("production", project_dir=project_dir)
    assert (project_dir / _PIN_FILENAME).exists()


def test_pin_profile_returns_path(project_dir):
    result = pin_profile("staging", project_dir=project_dir)
    assert isinstance(result, Path)
    assert result == project_dir / _PIN_FILENAME


def test_get_pinned_profile_returns_name(project_dir):
    pin_profile("staging", project_dir=project_dir)
    assert get_pinned_profile(project_dir=project_dir) == "staging"


def test_get_pinned_profile_none_when_no_pin(project_dir):
    assert get_pinned_profile(project_dir=project_dir) is None


def test_pin_overwrites_existing_pin(project_dir):
    pin_profile("dev", project_dir=project_dir)
    pin_profile("production", project_dir=project_dir)
    assert get_pinned_profile(project_dir=project_dir) == "production"


def test_unpin_removes_file(project_dir):
    pin_profile("dev", project_dir=project_dir)
    result = unpin_profile(project_dir=project_dir)
    assert result is True
    assert not (project_dir / _PIN_FILENAME).exists()


def test_unpin_returns_false_when_no_pin(project_dir):
    result = unpin_profile(project_dir=project_dir)
    assert result is False


def test_get_pinned_profile_returns_none_on_corrupt_file(project_dir):
    (project_dir / _PIN_FILENAME).write_text("not json", encoding="utf-8")
    assert get_pinned_profile(project_dir=project_dir) is None


def test_pin_profile_empty_name_raises(project_dir):
    with pytest.raises(ValueError):
        pin_profile("", project_dir=project_dir)


def test_pin_profile_whitespace_name_raises(project_dir):
    with pytest.raises(ValueError):
        pin_profile("   ", project_dir=project_dir)


def test_pin_profile_strips_whitespace(project_dir):
    pin_profile("  dev  ", project_dir=project_dir)
    assert get_pinned_profile(project_dir=project_dir) == "dev"
