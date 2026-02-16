"""
Input Validators - Generic validation for user input at system boundaries.

Parse at the boundary: validate and type-check all external input
before it enters the system. Never pass raw dicts or unvalidated
strings through multiple layers.

Reference: docs/AI_ENGINEERING_BEST_PRACTICES_2026.md (Part 7.2)

Keep this file under 100 lines.
"""

import logging
import re

logger = logging.getLogger(__name__)


class ValidationError(ValueError):
    """Raised when input validation fails. Contains a user-friendly message."""

    pass


def validate_not_empty(value: str, field_name: str = "input") -> str:
    """Validate that a string is not empty or whitespace-only."""
    if not value or not value.strip():
        raise ValidationError(f"{field_name} cannot be empty")
    return value.strip()


def validate_length(
    value: str,
    field_name: str = "input",
    min_length: int = 0,
    max_length: int = 100_000,
) -> str:
    """Validate string length is within bounds."""
    if len(value) < min_length:
        raise ValidationError(f"{field_name} must be at least {min_length} characters")
    if len(value) > max_length:
        raise ValidationError(f"{field_name} must be at most {max_length} characters")
    return value


def validate_identifier(value: str, field_name: str = "identifier") -> str:
    """Validate that a string is a safe identifier (alphanumeric + underscore)."""
    if not re.match(r"^[a-zA-Z][a-zA-Z0-9_-]*$", value):
        raise ValidationError(
            f"{field_name} must start with a letter and contain only "
            f"letters, numbers, underscores, and hyphens"
        )
    return value


def validate_in_choices(value: str, choices: list[str], field_name: str = "value") -> str:
    """Validate that a value is one of the allowed choices."""
    if value not in choices:
        raise ValidationError(f"{field_name} must be one of: {', '.join(choices)}")
    return value


def validate_positive_number(value: float | int, field_name: str = "number") -> float:
    """Validate that a number is positive."""
    if value <= 0:
        raise ValidationError(f"{field_name} must be positive (got {value})")
    return float(value)
