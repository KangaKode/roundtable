"""
Multi-agent orchestration.

Two interaction modes:
  - RoundTable: Full 4-phase deliberation (all agents, evidence-based consensus)
  - ChatOrchestrator: Lightweight real-time chat (1-3 agents, cross-checked)

Both use the same AgentProtocol, AgentRegistry, and LLM client with prompt caching.
"""
from .round_table import RoundTable, RoundTableConfig, AgentProtocol
from .chat_orchestrator import ChatOrchestrator, ChatConfig
from .agent_router import AgentRouter
