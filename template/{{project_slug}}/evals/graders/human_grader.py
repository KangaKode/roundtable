"""
Human Grader -- writes eval outputs for manual review.

Use for: gold-standard calibration, subjective quality assessment,
edge cases where code and model graders disagree.

Workflow:
  1. Eval generates agent output
  2. Human grader writes output + rubric to evals/human_review/
  3. Human reviews and marks pass/fail in the JSON file
  4. Results are loaded back for reporting

Reference: docs/REFERENCES.md (Anthropic Evals guide)
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

HUMAN_REVIEW_DIR = Path("evals/human_review")


@dataclass
class HumanGraderResult:
    """Result from human grading (pending until reviewed)."""

    eval_name: str
    passed: bool | None = None  # None = pending review
    reviewer: str = ""
    notes: str = ""
    reviewed_at: str = ""


class HumanGrader:
    """Writes eval outputs for manual human review.

    Usage:
        grader = HumanGrader("synthesis_quality")
        grader.submit_for_review(
            input_text="Analyze auth module",
            output_text=synthesis.recommended_direction,
            rubric="Is the recommendation actionable and evidence-based?"
        )
        # Human reviews evals/human_review/synthesis_quality_*.json
        # Then: result = grader.load_result("synthesis_quality_20260217.json")
    """

    def __init__(self, eval_name: str, review_dir: Path = HUMAN_REVIEW_DIR):
        self.eval_name = eval_name
        self._review_dir = review_dir

    def submit_for_review(
        self, input_text: str, output_text: str, rubric: str
    ) -> Path:
        """Write output + rubric to human review directory. Returns file path."""
        self._review_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.eval_name}_{timestamp}.json"
        filepath = self._review_dir / filename

        review_data = {
            "eval_name": self.eval_name,
            "submitted_at": datetime.now().isoformat(),
            "input_text": input_text[:5000],
            "output_text": output_text[:5000],
            "rubric": rubric,
            "status": "pending",
            "passed": None,
            "reviewer": "",
            "notes": "",
            "reviewed_at": "",
        }

        with open(filepath, "w") as f:
            json.dump(review_data, f, indent=2)

        logger.info(f"[HumanGrader] Review submitted: {filepath}")
        return filepath

    def load_result(self, filepath: Path) -> HumanGraderResult:
        """Load a completed human review."""
        with open(filepath) as f:
            data = json.load(f)

        return HumanGraderResult(
            eval_name=data.get("eval_name", self.eval_name),
            passed=data.get("passed"),
            reviewer=data.get("reviewer", ""),
            notes=data.get("notes", ""),
            reviewed_at=data.get("reviewed_at", ""),
        )
