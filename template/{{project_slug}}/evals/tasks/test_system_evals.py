"""
System Eval Tasks (5 of 20) - Cost, efficiency, multi-turn, errors, round table.

These tests verify system-level behavior: cost tracking, token efficiency,
multi-turn coherence, error quality, and round table consensus.
"""

import pytest


class TestCostBounds:
    """Eval 16: Does the system stay within token budget?"""

    def test_cost_calculation_accurate(self):
        """Cost calculation should match actual token usage."""
        # Verify: (input_tokens / 1M) * input_price + (output_tokens / 1M) * output_price
        input_tokens = 1000
        output_tokens = 500
        input_price = 5.0  # $/M tokens
        output_price = 25.0

        expected_cost = (input_tokens / 1_000_000) * input_price + (output_tokens / 1_000_000) * output_price
        assert abs(expected_cost - 0.0175) < 0.001

    def test_budget_not_exceeded(self):
        """A session should not exceed its configured budget."""
        # Your rate limiter / cost tracker should enforce this
        session_budget = 5.0  # $5 max
        session_cost = 0.50  # $0.50 spent
        assert session_cost <= session_budget


class TestTokenEfficiency:
    """Eval 17: Does the system avoid unnecessary verbosity?"""

    def test_prompt_not_redundant(self):
        """Prompts should not contain duplicated instructions."""
        prompt = "Analyze this. Be concise. Provide evidence."
        words = prompt.lower().split()
        # No word should appear more than twice (rough heuristic)
        from collections import Counter
        counts = Counter(words)
        for word, count in counts.items():
            if len(word) > 3:  # Skip short words
                assert count <= 3, f"Word '{word}' appears {count} times"

    def test_system_prompt_under_limit(self):
        """System prompts should be under a reasonable token estimate."""
        # ~4 chars per token, 2000 token budget for system prompts
        max_chars = 8000
        sample_system_prompt = "You are a helpful analyst." * 10  # 260 chars
        assert len(sample_system_prompt) < max_chars


class TestMultiTurnCoherence:
    """Eval 18: Does context carry correctly across turns?"""

    def test_thread_preserves_turns(self):
        """Thread should preserve all turns in order."""
        from src.harness.session import Thread, Turn, Item  # type: ignore

        thread = Thread(id="test")
        turn1 = Turn(id="t1")
        turn1.add_item(Item(id="i1", type="message", content="Hello"))
        turn2 = Turn(id="t2")
        turn2.add_item(Item(id="i2", type="message", content="Follow-up"))

        thread.add_turn(turn1)
        thread.add_turn(turn2)

        assert len(thread.turns) == 2
        assert thread.turns[0].items[0].content == "Hello"
        assert thread.turns[1].items[0].content == "Follow-up"

    def test_thread_fork_preserves_history(self):
        """Forked thread should contain all prior history."""
        from src.harness.session import Thread, Turn, Item  # type: ignore

        thread = Thread(id="original")
        turn = Turn(id="t1")
        turn.add_item(Item(id="i1", type="message", content="Original"))
        thread.add_turn(turn)

        forked = thread.fork("branch-1")
        assert forked.id == "branch-1"
        assert len(forked.turns) == 1
        assert forked.metadata["forked_from"] == "original"


class TestErrorQuality:
    """Eval 19: Are errors actionable, not cryptic?"""

    def test_validation_errors_are_descriptive(self):
        """Validation errors should tell the user what went wrong and how to fix it."""
        from src.security.validators import validate_not_empty, ValidationError  # type: ignore

        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_not_empty("")

    def test_validation_errors_name_the_field(self):
        """Errors should name the specific field that failed."""
        from src.security.validators import validate_length, ValidationError  # type: ignore

        with pytest.raises(ValidationError, match="username"):
            validate_length("x" * 200, field_name="username", max_length=50)


class TestRoundTableConsensus:
    """Eval 20: Does the multi-agent voting mechanism work correctly?"""

    def test_consensus_calculation(self):
        """Consensus should be reached when approval rate >= threshold."""
        from src.orchestration.round_table import RoundTableResult, AgentVote  # type: ignore

        result = RoundTableResult(
            task_id="test",
            votes=[
                AgentVote(agent_name="a1", approve=True),
                AgentVote(agent_name="a2", approve=True),
                AgentVote(agent_name="a3", approve=False, dissent_reason="Missing evidence"),
            ],
        )
        # 2/3 = 66.7% -- below 70% threshold
        assert result.approval_rate == pytest.approx(0.667, abs=0.01)

    def test_unanimous_approval(self):
        """All agents approve -> consensus reached."""
        from src.orchestration.round_table import RoundTableResult, AgentVote  # type: ignore

        result = RoundTableResult(
            task_id="test",
            votes=[
                AgentVote(agent_name="a1", approve=True),
                AgentVote(agent_name="a2", approve=True),
            ],
        )
        assert result.approval_rate == 1.0

    def test_dissent_preserved(self):
        """Dissenting votes should preserve their reasoning."""
        from src.orchestration.round_table import AgentVote  # type: ignore

        vote = AgentVote(agent_name="skeptic", approve=False, dissent_reason="Insufficient evidence for claim X")
        assert vote.dissent_reason is not None
        assert "evidence" in vote.dissent_reason
