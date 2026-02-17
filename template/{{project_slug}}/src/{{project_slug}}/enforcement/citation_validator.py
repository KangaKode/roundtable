"""
CitationValidator -- checks that cited sources actually exist.

Uses a pluggable SourceRegistry protocol so projects can wire in their
own data sources. Ships with a DefaultSourceRegistry that accepts all
sources (permissive mode for projects that haven't configured theirs yet).

Keep this file under 100 lines.
"""

import logging
import re
from typing import Protocol, runtime_checkable

from .models import ValidationResult, Violation

logger = logging.getLogger(__name__)

SOURCE_REF_PATTERN = re.compile(
    r"\[(VERIFIED|CORROBORATED|INDICATED):\s*([^\]]+)\]", re.IGNORECASE
)


@runtime_checkable
class SourceRegistry(Protocol):
    """Protocol for validating that cited sources exist.

    Projects implement this to connect their actual data sources.
    """

    def source_exists(self, source_name: str) -> bool:
        """Check if a named source is known to the system."""
        ...

    def reference_exists(self, source_name: str, reference: str) -> bool:
        """Check if a specific reference within a source exists."""
        ...


class DefaultSourceRegistry:
    """Permissive registry that accepts all sources.

    Used when a project hasn't configured its own source registry.
    Replace with your own implementation for real validation.
    """

    def source_exists(self, source_name: str) -> bool:
        return True

    def reference_exists(self, source_name: str, reference: str) -> bool:
        return True


class CitationValidator:
    """Validates that cited sources exist in the configured registry.

    Usage:
        validator = CitationValidator(registry=MySourceRegistry())
        result = validator.check("[VERIFIED: okta_logs:row_456] Event found")
    """

    def __init__(self, registry: SourceRegistry | None = None):
        self._registry = registry or DefaultSourceRegistry()

    def check(self, text: str) -> ValidationResult:
        """Validate all source citations in text."""
        violations = []

        for match in SOURCE_REF_PATTERN.finditer(text):
            level = match.group(1).upper()
            content = match.group(2).strip()

            if level == "VERIFIED" and ":" in content:
                parts = content.split(":", 1)
                source = parts[0].strip()
                reference = parts[1].strip()
                if not self._registry.source_exists(source):
                    violations.append(Violation(
                        rule="citation:unknown_source",
                        severity="critical",
                        message=f"Source '{source}' is not a known data source",
                        location=match.group(0),
                        suggestion=f"Verify that '{source}' is a valid source name",
                    ))
                elif not self._registry.reference_exists(source, reference):
                    violations.append(Violation(
                        rule="citation:unknown_reference",
                        severity="warning",
                        message=f"Reference '{reference}' in source '{source}' could not be verified",
                        location=match.group(0),
                        suggestion=f"Check that '{reference}' exists in '{source}'",
                    ))

        critical_count = sum(1 for v in violations if v.severity == "critical")
        outcome = "rejected" if critical_count > 0 else ("challenged" if violations else "accepted")
        return ValidationResult(outcome=outcome, violations=violations)
