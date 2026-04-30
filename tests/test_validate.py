"""Tests for stashenv.validate."""
import pytest
from pathlib import Path

from stashenv.validate import (
    ValidationRule,
    save_rules,
    load_rules,
    validate_env,
)


@pytest.fixture
def store_dir(tmp_path: Path) -> Path:
    return tmp_path


def test_validate_all_ok():
    rules = [ValidationRule(key="PORT", pattern=r"\d+")]
    result = validate_env({"PORT": "8080"}, rules)
    assert result.ok
    assert result.issues == []


def test_validate_missing_required_key():
    rules = [ValidationRule(key="SECRET", required=True)]
    result = validate_env({}, rules)
    assert not result.ok
    assert any("missing" in i.message for i in result.issues)


def test_validate_missing_optional_key_no_issue():
    rules = [ValidationRule(key="DEBUG", required=False)]
    result = validate_env({}, rules)
    assert result.ok


def test_validate_pattern_mismatch():
    rules = [ValidationRule(key="PORT", pattern=r"\d+")]
    result = validate_env({"PORT": "not-a-number"}, rules)
    assert not result.ok
    assert any("pattern" in i.message for i in result.issues)


def test_validate_allowed_values_pass():
    rules = [ValidationRule(key="ENV", allowed=["dev", "staging", "prod"])]
    result = validate_env({"ENV": "dev"}, rules)
    assert result.ok


def test_validate_allowed_values_fail():
    rules = [ValidationRule(key="ENV", allowed=["dev", "staging", "prod"])]
    result = validate_env({"ENV": "local"}, rules)
    assert not result.ok
    assert any("allowed" in i.message for i in result.issues)


def test_save_and_load_rules_roundtrip(store_dir: Path):
    rules = [
        ValidationRule(key="PORT", pattern=r"\d+", required=True),
        ValidationRule(key="ENV", allowed=["dev", "prod"], required=True),
    ]
    save_rules(store_dir, "myprofile", rules)
    loaded = load_rules(store_dir, "myprofile")
    assert len(loaded) == 2
    assert loaded[0].key == "PORT"
    assert loaded[0].pattern == r"\d+"
    assert loaded[1].allowed == ["dev", "prod"]


def test_load_rules_returns_empty_when_no_file(store_dir: Path):
    rules = load_rules(store_dir, "nonexistent")
    assert rules == []


def test_multiple_issues_collected():
    rules = [
        ValidationRule(key="PORT", pattern=r"\d+"),
        ValidationRule(key="SECRET", required=True),
    ]
    result = validate_env({"PORT": "abc"}, rules)
    assert len(result.issues) == 2
