"""Template support: render a stored profile with variable substitution."""

import re
from typing import Optional


class TemplateSyntaxError(ValueError):
    pass


class MissingVariableError(KeyError):
    pass


_VAR_RE = re.compile(r"\{\{\s*(\w+)\s*\}\}")


def render_template(template_text: str, variables: dict[str, str], strict: bool = True) -> str:
    """Render a .env template string by substituting {{ VAR }} placeholders.

    Args:
        template_text: Raw template content (may contain {{ KEY }} tokens).
        variables: Mapping of variable names to replacement values.
        strict: If True, raise MissingVariableError for unresolved placeholders.

    Returns:
        Rendered string with all placeholders replaced.
    """
    missing: list[str] = []

    def replace(match: re.Match) -> str:
        key = match.group(1)
        if key in variables:
            return variables[key]
        if strict:
            missing.append(key)
        return match.group(0)  # leave as-is in non-strict mode

    result = _VAR_RE.sub(replace, template_text)

    if missing:
        raise MissingVariableError(
            f"Template references undefined variables: {', '.join(sorted(missing))}"
        )

    return result


def extract_variables(template_text: str) -> list[str]:
    """Return a sorted list of unique variable names referenced in a template."""
    return sorted({m.group(1) for m in _VAR_RE.finditer(template_text)})


def validate_template(template_text: str) -> list[str]:
    """Check for malformed placeholders (e.g. unclosed braces).

    Returns a list of warning strings; empty list means the template looks fine.
    """
    warnings: list[str] = []
    # Check for single-brace patterns that look like forgotten {{ }}
    single_brace = re.compile(r"(?<!\{)\{(\w+)\}(?!\})")
    for m in single_brace.finditer(template_text):
        warnings.append(
            f"Possible unintended single-brace placeholder '{{{{ {m.group(1)} }}}}' at position {m.start()}"
        )
    return warnings
