"""Tests for stashenv.lint."""
import pytest
from pathlib import Path

from stashenv.lint import lint_text, lint_profile, lint_all_profiles, LintIssue
from stashenv.store import save_profile


@pytest.fixture
def store(tmp_path):
    return tmp_path


GOOD_ENV = "DB_HOST=localhost\nDB_PORT=5432\nSECRET_KEY=abc123\n"
BAD_ENV = "\n# comment\nNO_EQUALS_HERE\n DB_HOST =localhost\n"


def test_lint_text_clean_returns_no_issues():
    result = lint_text("prod", GOOD_ENV)
    assert result.issues == []
    assert result.ok is True


def test_lint_text_missing_equals_is_error():
    result = lint_text("prod", BAD_ENV)
    errors = [i for i in result.issues if i.severity == "error"]
    assert any("no '='" in i.message for i in errors)


def test_lint_text_key_with_space_is_error():
    result = lint_text("prod", " DB HOST =value\n")
    assert any("whitespace" in i.message for i in result.issues)


def test_lint_text_empty_value_is_warning():
    result = lint_text("prod", "MY_KEY=\n")
    warnings = [i for i in result.issues if i.severity == "warning"]
    assert any("empty value" in i.message for i in warnings)


def test_lint_text_duplicate_key_is_warning():
    env = "FOO=bar\nBAZ=qux\nFOO=other\n"
    result = lint_text("dev", env)
    warnings = [i for i in result.issues if i.severity == "warning"]
    assert any("Duplicate" in i.message for i in warnings)


def test_lint_text_key_starting_with_digit_is_warning():
    result = lint_text("dev", "1INVALID=val\n")
    assert any("invalid character" in i.message for i in result.issues)


def test_lint_text_ok_false_when_errors_present():
    result = lint_text("dev", "BROKEN\n")
    assert result.ok is False


def test_lint_profile_roundtrip(store):
    save_profile(store, "staging", GOOD_ENV, "pw")
    result = lint_profile(store, "staging", "pw")
    assert result.profile == "staging"
    assert result.issues == []


def test_lint_all_profiles(store):
    save_profile(store, "a", GOOD_ENV, "pw")
    save_profile(store, "b", GOOD_ENV, "pw")
    results = lint_all_profiles(store, "pw")
    assert len(results) == 2
    assert all(r.ok for r in results)


def test_lint_issue_has_line_number():
    result = lint_text("dev", "FIRST=ok\nBAD LINE\nSECOND=ok\n")
    error = next(i for i in result.issues if i.severity == "error")
    assert error.line == 2


def test_lint_all_profiles_mixed_results(store):
    """Verify lint_all_profiles captures issues from profiles that have errors."""
    save_profile(store, "good", GOOD_ENV, "pw")
    save_profile(store, "bad", BAD_ENV, "pw")
    results = lint_all_profiles(store, "pw")
    assert len(results) == 2
    good_result = next(r for r in results if r.profile == "good")
    bad_result = next(r for r in results if r.profile == "bad")
    assert good_result.ok is True
    assert bad_result.ok is False
