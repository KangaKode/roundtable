"""
Model-Based Graders - LLM-as-judge for subjective evaluation.

Use when output is freeform text where code-based matching is too brittle.
Always pair with a rubric to constrain the judge.

Reference: docs/AI_ENGINEERING_BEST_PRACTICES_2026.md (Part 5.3)

Keep this file under 100 lines.
"""

import json
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

RUBRIC_TEMPLATE = """You are an evaluation judge. Score the following output.

## Rubric
{rubric}

## Input Given to Agent
{input_text}

## Agent Output
{output_text}

## Instructions
Return ONLY valid JSON: {{"score": <float 0.0-1.0>, "passed": <bool>, "reasoning": "<1-2 sentences>"}}
"""


@dataclass
class ModelGraderConfig:
    """Configuration for a model-based grader."""

    eval_name: str
    rubric: str
    pass_threshold: float = 0.7
    judge_role: str = "specialist"


@dataclass
class ModelGraderResult:
    """Result from model-based grading."""

    eval_name: str
    passed: bool
    score: float
    reasoning: str = ""


async def grade_with_model(
    llm_client,
    config: ModelGraderConfig,
    input_text: str,
    output_text: str,
) -> ModelGraderResult:
    """Run model-based grading with a rubric. Requires an LLM client."""
    prompt = RUBRIC_TEMPLATE.format(
        rubric=config.rubric,
        input_text=input_text[:2000],
        output_text=output_text[:2000],
    )

    try:
        response = await llm_client.call(
            prompt=prompt, role=config.judge_role, temperature=0.0, max_tokens=256,
        )
        data = json.loads(response.content)
        return ModelGraderResult(
            eval_name=config.eval_name,
            passed=data.get("score", 0) >= config.pass_threshold,
            score=data.get("score", 0),
            reasoning=data.get("reasoning", ""),
        )
    except (json.JSONDecodeError, Exception) as e:
        logger.warning(f"[ModelGrader] {config.eval_name} failed: {e}")
        return ModelGraderResult(eval_name=config.eval_name, passed=False, score=0.0,
                                 reasoning=f"Grading failed: {e}")
