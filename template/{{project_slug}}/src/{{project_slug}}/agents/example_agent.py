"""
Example Agent - Shows how to implement AgentProtocol for the Round Table.

Copy this file and customize for your project's specialist agents.
Each agent needs: name, domain, analyze(), challenge(), vote().

Uses CacheablePrompt so the system instructions (agent role, evidence rules)
are cached across calls -- saving ~90% on input tokens for the stable prefix.

Reference: src/orchestration/round_table.py
Reference: src/llm/client.py (CacheablePrompt)
"""

import json
import logging

from ..llm import CacheablePrompt
from ..orchestration.round_table import (
    AgentAnalysis,
    AgentChallenge,
    AgentVote,
    RoundTableTask,
    SynthesisResult,
)

logger = logging.getLogger(__name__)


class ExampleAgent:
    """
    Example agent implementing the AgentProtocol.

    Replace this with your own specialist agents. Each agent should:
    1. Have a clear domain (what it analyzes)
    2. Cite evidence for every finding
    3. Stay within its domain boundaries
    4. Challenge other agents with counter-evidence, not opinions
    """

    def __init__(self, llm_client=None):
        self._llm = llm_client

    @property
    def name(self) -> str:
        return "example_analyst"

    @property
    def domain(self) -> str:
        return "general analysis"

    def _system_prompt(self) -> str:
        """Stable system prompt (cached across calls for token savings)."""
        return (
            f"You are a {self.domain} specialist.\n\n"
            f"For EACH finding, you MUST provide:\n"
            f"- finding: what you observed\n"
            f"- evidence: specific quote or data supporting your finding\n"
            f"- severity: critical / warning / info\n"
            f"- confidence: 0.0 to 1.0\n\n"
            f"Always return valid JSON."
        )

    async def analyze(self, task: RoundTableTask) -> AgentAnalysis:
        """Phase 1: Independent analysis. Cite evidence for every finding."""
        if not self._llm:
            return AgentAnalysis(
                agent_name=self.name,
                domain=self.domain,
                observations=[{
                    "finding": "Example finding -- replace with real analysis",
                    "evidence": "No LLM client configured",
                    "severity": "info",
                    "confidence": 0.0,
                }],
            )

        prompt = CacheablePrompt(
            system=self._system_prompt(),
            user_message=(
                f"Analyze the following:\n{task.content}\n\n"
                f'Return JSON: {{"observations": [...], "recommendations": [...]}}'
            ),
        )

        response = await self._llm.call(prompt=prompt, role="specialist")

        try:
            data = json.loads(response.content)
            return AgentAnalysis(
                agent_name=self.name,
                domain=self.domain,
                observations=data.get("observations", []),
                recommendations=data.get("recommendations", []),
                raw_response=response.content,
            )
        except json.JSONDecodeError:
            return AgentAnalysis(
                agent_name=self.name,
                domain=self.domain,
                observations=[{"finding": response.content[:500], "evidence": "raw response",
                               "severity": "info", "confidence": 0.5}],
                raw_response=response.content,
            )

    async def challenge(
        self, task: RoundTableTask, other_analyses: list[AgentAnalysis]
    ) -> AgentChallenge:
        """Phase 2: Challenge other agents with evidence, not opinions."""
        return AgentChallenge(agent_name=self.name)

    async def vote(
        self, task: RoundTableTask, synthesis: SynthesisResult
    ) -> AgentVote:
        """Phase 3: Vote on synthesis. Dissent is valuable -- explain why."""
        return AgentVote(agent_name=self.name, approve=True)
