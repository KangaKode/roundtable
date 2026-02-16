"""
Vanilla Learning System -- teaches your AI agent project to learn from user interactions.

Core (Phase 4):
  - models.py: Data models (FeedbackSignal, UserPreference, AgentTrustScore, CheckIn)
  - schema.py: Database schema creation and migration
  - feedback_tracker.py: Records accept/reject/modify signals (SQLite)
  - agent_trust.py: Trust scores per agent with EMA scoring
  - checkin_manager.py: Permission-based adaptation gates

RAG + Profile (Phase 5):
  - rag/vector_store.py: ChromaDB wrapper with in-memory fallback
  - rag/embedding_service.py: Multi-provider embeddings with caching
  - rag/preference_retriever.py: Semantic search over learned preferences
  - user_profile.py: Aggregation into context bundles for LLM prompts
  - global_profile.py: Cross-project identity (~/.aiscaffold/)
  - graduation.py: Promote stable patterns to global level

All terminology is vanilla -- "user", "agent", "preference", "feedback", "session".
Domain-specific vocabulary is added by the project, not the scaffold.
"""

from .models import (
    FeedbackSignal,
    UserPreference,
    AgentTrustScore,
    CheckIn,
    SignalType,
    CheckInStatus,
)
from .feedback_tracker import FeedbackTracker
from .agent_trust import AgentTrustManager
from .checkin_manager import CheckInManager
from .user_profile import UserProfileManager
from .global_profile import GlobalProfileManager
from .graduation import GraduationEngine, GraduationRule, GraduationCandidate
