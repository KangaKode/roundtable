"""
FactChecker -- scans agent responses for banned speculation and opinion patterns.

Banned categories:
  - Numeric confidence: "90% confident", "confidence: 0.85", "HIGH confidence"
  - Speculation: "likely indicates", "probably", "this suggests", "it appears that"
  - Opinion: "I think", "I believe", "in my opinion"
  - Hedging: "this could mean", "seems to", "may indicate", "might be"

Design principle: investigators may testify to these findings.
"VERIFIED in source row 456" holds up. "85% confident" does not.

Keep this file under 150 lines.
"""

import logging
import re

from .models import ValidationResult, Violation

logger = logging.getLogger(__name__)

BANNED_PATTERNS: dict[str, list[dict]] = {
    "numeric_confidence": [
        {"pattern": r"\d+%\s*confident", "message": "No percentage confidence scores", "severity": "critical"},
        {"pattern": r"confidence[:\s]+0?\.\d+", "message": "No decimal confidence values", "severity": "critical"},
        {"pattern": r"\b(HIGH|MEDIUM|LOW)\s+confidence\b", "message": "No categorical confidence labels", "severity": "critical"},
    ],
    "speculation": [
        {"pattern": r"\blikely\s+indicates?\b", "message": "No speculation -- cite evidence instead", "severity": "critical"},
        {"pattern": r"\bprobably\b", "message": "No speculation -- state what the evidence shows", "severity": "critical"},
        {"pattern": r"\bthis\s+suggests\b", "message": "No speculation -- use evidence levels (VERIFIED/INDICATED)", "severity": "critical"},
        {"pattern": r"\bit\s+appears\s+that\b", "message": "No speculation -- state facts with evidence", "severity": "critical"},
        {"pattern": r"\bstrongly\s+suggests?\b", "message": "No speculation -- use CORROBORATED if multiple sources agree", "severity": "warning"},
    ],
    "opinion": [
        {"pattern": r"\bI\s+think\b", "message": "No opinions -- only evidence-based findings", "severity": "critical"},
        {"pattern": r"\bI\s+believe\b", "message": "No opinions -- cite what the data shows", "severity": "critical"},
        {"pattern": r"\bin\s+my\s+opinion\b", "message": "No opinions -- use evidence levels", "severity": "critical"},
    ],
    "hedging": [
        {"pattern": r"\bthis\s+could\s+mean\b", "message": "No hedging -- use [POSSIBLE] if uncertain", "severity": "warning"},
        {"pattern": r"\bseems?\s+to\b", "message": "No hedging -- state what the evidence shows", "severity": "warning"},
        {"pattern": r"\bmay\s+indicate\b", "message": "No hedging -- use [INDICATED] with source name", "severity": "warning"},
        {"pattern": r"\bmight\s+be\b", "message": "No hedging -- use [POSSIBLE] if unconfirmed", "severity": "warning"},
        {"pattern": r"\bcould\s+be\b", "message": "No hedging -- use [POSSIBLE] if unconfirmed", "severity": "warning"},
    ],
}

CRITICAL_THRESHOLD = 3


class FactChecker:
    """Scans agent response text for banned speculation and opinion patterns.

    Usage:
        checker = FactChecker()
        result = checker.check("The data probably indicates a breach")
        # result.outcome == "rejected" (contains "probably")
    """

    def check(self, text: str) -> ValidationResult:
        """Scan text for banned patterns. Returns ValidationResult."""
        violations = []

        for category, patterns in BANNED_PATTERNS.items():
            for entry in patterns:
                matches = list(re.finditer(entry["pattern"], text, re.IGNORECASE))
                for match in matches:
                    violations.append(Violation(
                        rule=f"banned_pattern:{category}",
                        severity=entry["severity"],
                        message=entry["message"],
                        location=match.group(0),
                        suggestion=self._suggest_fix(category, match.group(0)),
                    ))

        critical_count = sum(1 for v in violations if v.severity == "critical")

        if critical_count >= CRITICAL_THRESHOLD:
            outcome = "rejected"
        elif critical_count > 0:
            outcome = "challenged"
        elif violations:
            outcome = "challenged"
        else:
            outcome = "accepted"

        if violations:
            logger.debug(
                f"[FactChecker] {len(violations)} violations "
                f"({critical_count} critical): {outcome}"
            )

        return ValidationResult(outcome=outcome, violations=violations)

    def _suggest_fix(self, category: str, matched_text: str) -> str:
        """Generate a fix suggestion based on the violation category."""
        suggestions = {
            "numeric_confidence": (
                f"Remove '{matched_text}'. Use evidence levels instead: "
                f"[VERIFIED: source:ref], [CORROBORATED: src1 + src2], "
                f"[INDICATED: source], or [POSSIBLE]"
            ),
            "speculation": (
                f"Replace '{matched_text}' with a factual statement. "
                f"If uncertain, use [INDICATED: source] or [POSSIBLE]"
            ),
            "opinion": (
                f"Replace '{matched_text}' with what the evidence shows. "
                f"Cite the specific source and reference."
            ),
            "hedging": (
                f"Replace '{matched_text}' with an evidence level tag: "
                f"[INDICATED: source] if data exists, [POSSIBLE] if not"
            ),
        }
        return suggestions.get(category, f"Remove '{matched_text}' and cite evidence")
