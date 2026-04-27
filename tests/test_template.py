"""Tests for stashenv.template."""

import pytest

from stashenv.template import (
    MissingVariableError,
    TemplateSyntaxError,
    extract_variables,
    render_template,
    validate_template,
)


SAMPLE_TEMPLATE = """DB_HOST={{ HOST }}
DB_PORT={{ PORT }}
DB_USER={{ USER }}
DB_PASS={{ PASS }}
"""


def test_render_basic_substitution():
    result = render_template("API_URL={{ URL }}", {"URL": "https://example.com"})
    assert result == "API_URL=https://example.com"


def test_render_multiple_placeholders():
    vars_ = {"HOST": "localhost", "PORT": "5432", "USER": "admin", "PASS": "secret"}
    result = render_template(SAMPLE_TEMPLATE, vars_)
    assert "DB_HOST=localhost" in result
    assert "DB_PORT=5432" in result
    assert "DB_USER=admin" in result
    assert "DB_PASS=secret" in result


def test_render_strict_raises_on_missing_variable():
    with pytest.raises(MissingVariableError) as exc_info:
        render_template("KEY={{ MISSING }}", {}, strict=True)
    assert "MISSING" in str(exc_info.value)


def test_render_non_strict_leaves_placeholder():
    result = render_template("KEY={{ MISSING }}", {}, strict=False)
    assert "{{ MISSING }}" in result


def test_render_whitespace_in_placeholder():
    result = render_template("X={{  FOO  }}", {"FOO": "bar"})
    assert result == "X=bar"


def test_render_no_placeholders_unchanged():
    text = "PLAIN=value\nOTHER=123\n"
    assert render_template(text, {}) == text


def test_render_reports_all_missing_variables():
    with pytest.raises(MissingVariableError) as exc_info:
        render_template("A={{ X }}\nB={{ Y }}", {}, strict=True)
    msg = str(exc_info.value)
    assert "X" in msg
    assert "Y" in msg


def test_extract_variables_basic():
    vars_ = extract_variables(SAMPLE_TEMPLATE)
    assert vars_ == ["HOST", "PASS", "PORT", "USER"]


def test_extract_variables_empty_template():
    assert extract_variables("NO_VARS=true") == []


def test_extract_variables_deduplicates():
    result = extract_variables("A={{ X }}\nB={{ X }}\nC={{ Y }}")
    assert result == ["X", "Y"]


def test_validate_template_clean_returns_empty():
    assert validate_template(SAMPLE_TEMPLATE) == []


def test_validate_template_warns_on_single_brace():
    warnings = validate_template("KEY={VALUE}")
    assert len(warnings) == 1
    assert "VALUE" in warnings[0]


def test_validate_template_no_false_positive_on_double_brace():
    warnings = validate_template("KEY={{ VALUE }}")
    assert warnings == []
