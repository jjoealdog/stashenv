"""Schema enforcement for .env profiles.

Allows defining expected keys with optional type hints and
default values, then validating a loaded profile against that schema.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class SchemaField:
    name: str
    required: bool = True
    default: str | None = None
    description: str = ""


@dataclass
class SchemaViolation:
    field: str
    message: str


def _schema_path(store_dir: Path) -> Path:
    return store_dir / ".schema.json"


def load_schema(store_dir: Path) -> list[SchemaField]:
    path = _schema_path(store_dir)
    if not path.exists():
        return []
    data = json.loads(path.read_text())
    return [
        SchemaField(
            name=entry["name"],
            required=entry.get("required", True),
            default=entry.get("default"),
            description=entry.get("description", ""),
        )
        for entry in data
    ]


def save_schema(store_dir: Path, fields: list[SchemaField]) -> None:
    path = _schema_path(store_dir)
    store_dir.mkdir(parents=True, exist_ok=True)
    data = [
        {
            "name": f.name,
            "required": f.required,
            "default": f.default,
            "description": f.description,
        }
        for f in fields
    ]
    path.write_text(json.dumps(data, indent=2))


def validate_against_schema(
    env: dict[str, str], fields: list[SchemaField]
) -> list[SchemaViolation]:
    violations: list[SchemaViolation] = []
    for field in fields:
        if field.name not in env:
            if field.required and field.default is None:
                violations.append(
                    SchemaViolation(
                        field=field.name,
                        message=f"required key '{field.name}' is missing and has no default",
                    )
                )
    return violations


def apply_defaults(env: dict[str, str], fields: list[SchemaField]) -> dict[str, str]:
    """Return a copy of env with schema defaults filled in for missing keys."""
    result = dict(env)
    for f in fields:
        if f.name not in result and f.default is not None:
            result[f.name] = f.default
    return result
