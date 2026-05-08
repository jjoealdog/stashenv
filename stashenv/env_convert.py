"""Convert .env profiles between formats: dotenv, JSON, YAML export/import."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from stashenv.store import load_profile, save_profile


class ProfileNotFoundError(Exception):
    pass


class UnsupportedFormatError(Exception):
    pass


SUPPORTED_FORMATS = ("dotenv", "json", "yaml")


def _parse_env_text(text: str) -> Dict[str, str]:
    result: Dict[str, str] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        result[key.strip()] = value.strip()
    return result


def _unparse_env_text(data: Dict[str, str]) -> str:
    return "\n".join(f"{k}={v}" for k, v in data.items()) + "\n"


def export_as(store_dir: Path, profile: str, password: str, fmt: str) -> str:
    """Export a profile as the given format string. Returns the serialised text."""
    if fmt not in SUPPORTED_FORMATS:
        raise UnsupportedFormatError(f"Format '{fmt}' is not supported. Choose from: {SUPPORTED_FORMATS}")

    raw = load_profile(store_dir, profile, password)
    data = _parse_env_text(raw)

    if fmt == "dotenv":
        return _unparse_env_text(data)

    if fmt == "json":
        return json.dumps(data, indent=2) + "\n"

    if fmt == "yaml":
        lines = []
        for k, v in data.items():
            safe_v = f"'{v}'" if any(c in v for c in (":", "#", "{", "}")) else v
            lines.append(f"{k}: {safe_v}")
        return "\n".join(lines) + "\n"

    raise UnsupportedFormatError(fmt)  # pragma: no cover


def import_from(store_dir: Path, profile: str, password: str, text: str, fmt: str) -> None:
    """Parse text in the given format and save it as a profile."""
    if fmt not in SUPPORTED_FORMATS:
        raise UnsupportedFormatError(f"Format '{fmt}' is not supported. Choose from: {SUPPORTED_FORMATS}")

    if fmt == "dotenv":
        data = _parse_env_text(text)

    elif fmt == "json":
        data = json.loads(text)
        if not isinstance(data, dict):
            raise ValueError("JSON input must be an object/dict at the top level")

    elif fmt == "yaml":
        data = {}
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if ":" not in stripped:
                continue
            key, _, value = stripped.partition(":")
            data[key.strip()] = value.strip().strip("'\"")

    env_text = _unparse_env_text(data)
    save_profile(store_dir, profile, password, env_text)
