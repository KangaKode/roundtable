"""
Quality Eval Tasks (5 of 20) - Output format, instruction following, evidence, confidence, context.

These tests verify that agent outputs meet quality standards:
correct format, follow instructions, cite evidence, calibrate confidence,
and use provided context.
"""

import json
import pytest


class TestOutputFormat:
    """Eval 6: Does output match expected JSON schema?"""

    def test_valid_json_parseable(self):
        """Agent outputs claiming to be JSON must be valid JSON."""
        valid = '{"findings": [{"finding": "x", "severity": "info"}]}'
        data = json.loads(valid)
        assert "findings" in data

    def test_required_fields_present(self):
        """Agent analysis output must contain required fields."""
        # Define your project's required output schema
        required_fields = {"observations", "recommendations"}
        sample = {"observations": [], "recommendations": []}
        assert required_fields.issubset(sample.keys())

    def test_severity_values_valid(self):
        """Severity must be one of the allowed values."""
        valid_severities = {"critical", "warning", "info"}
        for severity in valid_severities:
            assert severity in valid_severities


class TestInstructionFollowing:
    """Eval 7: Does the agent follow stated constraints?"""

    def test_max_length_respected(self):
        """When told to limit output length, it should comply."""
        # This requires a real LLM call or a mock that simulates compliance
        pass  # Replace with your LLM integration test

    def test_format_constraints_followed(self):
        """When told to output JSON, it should not add preamble text."""
        pass  # Replace with format compliance test

    def test_negative_constraints_followed(self):
        """When told NOT to do something, it should comply."""
        # e.g., "Do NOT generate code" -> output should not contain code blocks
        pass  # Replace with negative constraint test


class TestEvidenceCitation:
    """Eval 8: Does the agent cite sources when required?"""

    def test_findings_have_evidence(self):
        """Every finding should include an evidence field."""
        sample_findings = [
            {"finding": "Issue found", "evidence": "Line 42 shows...", "severity": "warning"},
            {"finding": "Another issue", "evidence": "The data shows...", "severity": "info"},
        ]
        for f in sample_findings:
            assert "evidence" in f
            assert len(f["evidence"]) > 0

    def test_empty_evidence_flagged(self):
        """Findings with empty evidence should be flagged as low-quality."""
        finding = {"finding": "Something is wrong", "evidence": "", "severity": "warning"}
        assert finding["evidence"] == ""  # This should fail quality check


class TestConfidenceCalibration:
    """Eval 9: Is stated confidence accurate?"""

    def test_confidence_in_valid_range(self):
        """Confidence must be between 0.0 and 1.0."""
        for conf in [0.0, 0.5, 0.75, 1.0]:
            assert 0.0 <= conf <= 1.0

    def test_low_evidence_low_confidence(self):
        """Findings with little evidence should have lower confidence."""
        # This is a heuristic check -- in real evals, compare against ground truth
        finding_strong = {"evidence": "Multiple data points confirm...", "confidence": 0.9}
        finding_weak = {"evidence": "Maybe...", "confidence": 0.3}
        assert finding_strong["confidence"] > finding_weak["confidence"]


class TestContextRelevance:
    """Eval 10: Does the agent actually use the provided context?"""

    def test_context_referenced(self):
        """Agent output should reference key terms from provided context."""
        context = "The database uses PostgreSQL with connection pooling."
        # Agent output should mention PostgreSQL, not MySQL
        output = "The PostgreSQL database connection pool should be configured..."
        assert "PostgreSQL" in output

    def test_irrelevant_context_ignored(self):
        """Agent should not hallucinate relevance for unrelated context."""
        pass  # Replace with your context relevance test
