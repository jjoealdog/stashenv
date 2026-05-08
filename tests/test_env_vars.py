"""Tests for stashenv.env_vars interpolation module."""

import pytest

from stashenv.env_vars import (
    InterpolateResult,
    UnresolvedVariableError,
    interpolate_profile,
    interpolate_text,
)


# ---------------------------------------------------------------------------
# interpolate_text
# ---------------------------------------------------------------------------

SIMPLE = """HOST=localhost
PORT=5432
URL=${HOST}:${PORT}
"""


def test_basic_interpolation():
    result = interpolate_text(SIMPLE)
    assert result.expanded["URL"] == "localhost:5432"


def test_non_referenced_keys_unchanged():
    result = interpolate_text(SIMPLE)
    assert result.expanded["HOST"] == "localhost"
    assert result.expanded["PORT"] == "5432"


def test_ok_true_when_all_resolved():
    result = interpolate_text(SIMPLE)
    assert result.ok is True
    assert result.unresolved == []


def test_unresolved_left_in_place_non_strict():
    text = "URL=${MISSING_VAR}/path"
    result = interpolate_text(text, strict=False)
    assert result.expanded["URL"] == "${MISSING_VAR}/path"
    assert "MISSING_VAR" in result.unresolved


def test_ok_false_when_unresolved():
    text = "URL=${GHOST}"
    result = interpolate_text(text)
    assert result.ok is False


def test_strict_raises_on_missing_var():
    text = "URL=${GHOST}"
    with pytest.raises(UnresolvedVariableError, match="GHOST"):
        interpolate_text(text, strict=True)


def test_context_overrides_self_reference():
    text = "HOST=localhost\nURL=${HOST}:8080"
    result = interpolate_text(text, context={"HOST": "example.com"})
    assert result.expanded["URL"] == "example.com:8080"


def test_dollar_without_braces():
    text = "HOST=db\nURL=$HOST/mydb"
    result = interpolate_text(text)
    assert result.expanded["URL"] == "db/mydb"


def test_blank_lines_and_comments_ignored():
    text = "# comment\n\nKEY=value\n"
    result = interpolate_text(text)
    assert list(result.expanded.keys()) == ["KEY"]


def test_value_with_equals_sign():
    text = "DSN=host=localhost dbname=test"
    result = interpolate_text(text)
    assert result.expanded["DSN"] == "host=localhost dbname=test"


# ---------------------------------------------------------------------------
# interpolate_profile (integration)
# ---------------------------------------------------------------------------


def test_interpolate_profile_roundtrip(tmp_path):
    from stashenv.store import save_profile

    text = "BASE=http://localhost\nAPI=${BASE}/v1"
    save_profile("dev", text, "secret", tmp_path)
    result = interpolate_profile("dev", "secret", tmp_path)
    assert result.expanded["API"] == "http://localhost/v1"


def test_interpolate_profile_with_context(tmp_path):
    from stashenv.store import save_profile

    text = "URL=${HOST}/api"
    save_profile("prod", text, "pw", tmp_path)
    result = interpolate_profile("prod", "pw", tmp_path, context={"HOST": "prod.example.com"})
    assert result.expanded["URL"] == "prod.example.com/api"
