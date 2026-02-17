# Evaluation Guide

How to write evals for your AI agents. Based on [Anthropic: Demystifying Evals for AI Agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents).

---

## Core Principle

> **"Grade what the agent produced, not the path it took."**

Don't check that agents followed specific steps. Check that the output meets quality criteria.

---

## Three Types of Graders

| Type | Best For | Trade-offs |
|------|----------|------------|
| **Code-based** | Pass/fail, schema validation, threshold checks | Fast, cheap, reproducible; brittle to valid variations |
| **Model-based** | Freeform output, nuance, rubric scoring | Handles nuance; expensive, non-deterministic |
| **Human** | Gold standard calibration, edge cases | Slow, expensive; essential for calibration |

### Code-Based Grader

```python
from evals.graders import CodeGrader

grader = CodeGrader("round_table_consensus")
grader.add_check("has_analyses", lambda r: len(r.analyses) > 0)
grader.add_check("consensus_reached", lambda r: r.consensus_reached)
grader.add_check("has_synthesis", lambda r: r.synthesis is not None)
result = grader.grade(round_table_result)
# result.passed, result.checks_passed, result.failures
```

### Model-Based Grader

```python
from evals.graders import ModelGraderConfig, grade_with_model

config = ModelGraderConfig(
    eval_name="synthesis_quality",
    rubric="Is the recommendation specific, actionable, and supported by evidence?",
    pass_threshold=0.7,
)
result = await grade_with_model(llm_client, config, input_text, output_text)
# result.passed, result.score, result.reasoning
```

### Human Grader

```python
from evals.graders import HumanGrader

grader = HumanGrader("edge_case_review")
filepath = grader.submit_for_review(
    input_text="Ambiguous query about auth",
    output_text=agent_response,
    rubric="Did the agent correctly identify the ambiguity and ask for clarification?",
)
# Human reviews evals/human_review/edge_case_review_*.json
# Mark "passed": true/false, add "reviewer" and "notes"
```

---

## Getting Started: Your First 20 Evals

> "20-50 simple tasks drawn from real failures is a great start."

Sources for eval tasks:
1. **Bugs you've already fixed** -- turn each into a regression eval
2. **Manual checks you do before release** -- automate them
3. **Known failure modes** -- edge cases, adversarial inputs
4. **User complaints** -- real-world quality issues

### Graduation Pattern

Capability evals that consistently pass become regression evals:
1. Write a capability eval for a new feature
2. Run it repeatedly as the feature matures
3. When it passes 10+ times consecutively, promote to regression
4. Regression evals must maintain ~100% pass rate

The `learning/graduation.py` module implements this pattern.

---

## Running Evals

```bash
make eval              # Run all evals (mock LLM by default)
make eval-regression   # Regression evals only (must pass)
EVAL_USE_REAL_LLM=1 make eval  # Run with real LLM (needs API key)
```

---

## Directory Structure

```
evals/
  graders/
    code_grader.py      # Deterministic checks
    model_graders.py    # LLM-as-judge
    human_grader.py     # Manual review interface
  tasks/
    test_security_evals.py     # Security capability evals
    test_quality_evals.py      # Output quality evals
    test_reliability_evals.py  # Reliability and consistency evals
    test_system_evals.py       # System integration evals
  fixtures/
    sample_inputs.json  # Example inputs for evals
  regression/           # Graduated evals (must pass)
  results/              # Eval run results
  human_review/         # Pending human reviews
```
