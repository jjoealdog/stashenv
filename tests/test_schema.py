import json
import pytest
from pathlib import Path
from stashenv.schema import (
    SchemaField,
    load_schema,
    save_schema,
    validate_against_schema,
    apply_defaults,
)


@pytest.fixture
def store_dir(tmp_path):
    return tmp_path


def test_load_schema_returns_empty_when_no_file(store_dir):
    assert load_schema(store_dir) == []


def test_save_and_load_schema_roundtrip(store_dir):
    fields = [
        SchemaField(name="DATABASE_URL", required=True, description="Postgres URL"),
        SchemaField(name="DEBUG", required=False, default="false"),
    ]
    save_schema(store_dir, fields)
    loaded = load_schema(store_dir)
    assert len(loaded) == 2
    assert loaded[0].name == "DATABASE_URL"
    assert loaded[0].required is True
    assert loaded[1].name == "DEBUG"
    assert loaded[1].default == "false"


def test_save_schema_creates_json_file(store_dir):
    save_schema(store_dir, [SchemaField(name="FOO")])
    schema_file = store_dir / ".schema.json"
    assert schema_file.exists()
    data = json.loads(schema_file.read_text())
    assert isinstance(data, list)
    assert data[0]["name"] == "FOO"


def test_validate_no_violations_when_all_keys_present(store_dir):
    fields = [SchemaField(name="KEY_A"), SchemaField(name="KEY_B")]
    env = {"KEY_A": "1", "KEY_B": "2"}
    violations = validate_against_schema(env, fields)
    assert violations == []


def test_validate_detects_missing_required_key(store_dir):
    fields = [SchemaField(name="SECRET", required=True)]
    violations = validate_against_schema({}, fields)
    assert len(violations) == 1
    assert violations[0].field == "SECRET"


def test_validate_no_violation_for_optional_missing_key(store_dir):
    fields = [SchemaField(name="OPTIONAL", required=False)]
    violations = validate_against_schema({}, fields)
    assert violations == []


def test_validate_no_violation_when_missing_key_has_default(store_dir):
    fields = [SchemaField(name="PORT", required=True, default="8080")]
    violations = validate_against_schema({}, fields)
    assert violations == []


def test_apply_defaults_fills_missing_keys(store_dir):
    fields = [SchemaField(name="PORT", default="8080"), SchemaField(name="HOST", default="localhost")]
    result = apply_defaults({}, fields)
    assert result["PORT"] == "8080"
    assert result["HOST"] == "localhost"


def test_apply_defaults_does_not_overwrite_existing(store_dir):
    fields = [SchemaField(name="PORT", default="8080")]
    result = apply_defaults({"PORT": "9000"}, fields)
    assert result["PORT"] == "9000"


def test_apply_defaults_skips_fields_with_no_default(store_dir):
    fields = [SchemaField(name="SECRET", required=True, default=None)]
    result = apply_defaults({}, fields)
    assert "SECRET" not in result
