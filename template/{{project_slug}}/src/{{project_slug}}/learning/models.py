"""
Vanilla learning data models -- domain-agnostic building blocks.

All categories and types are strings (not enums) so projects define their
own taxonomy without modifying scaffold code. The only constants are the
universal signal types that every project needs.

Keep this file under 200 lines.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


# =============================================================================
# SIGNAL TYPES (universal across all domains)
# =============================================================================


class SignalType:
    """Universal feedback signal types. Projects can add their own as strings."""

    ACCEPT = "accept"
    REJECT = "reject"
    MODIFY = "modify"
    RATE = "rate"
    DISMISS = "dismiss"
    ESCALATE = "escalate"


class CheckInStatus:
    """Check-in lifecycle states."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    SKIPPED = "skipped"


# =============================================================================
# FEEDBACK SIGNAL
# =============================================================================


@dataclass
class FeedbackSignal:
    """
    Atomic feedback unit -- records a user's reaction to an agent output.

    signal_type: One of SignalType constants or a custom string.
    context_type: What was the agent output? E.g., "chat", "round_table",
                  "suggestion", "generated_content". Projects define their own.
    agent_id: Which agent produced the output (optional).
    content: The specific content the user reacted to (optional, for audit).
    metadata: Arbitrary key-value pairs for domain-specific data.
    """

    signal_type: str
    project_id: str = "default"
    context_type: str = ""
    agent_id: str = ""
    content: str = ""
    confidence: float = 0.5
    metadata: dict[str, Any] = field(default_factory=dict)
    session_id: str = ""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:12])
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


# =============================================================================
# USER PREFERENCE
# =============================================================================


@dataclass
class UserPreference:
    """
    A learned preference -- key-value pair with priority and source.

    preference_type: Category string. E.g., "style", "behavior", "output_format".
    key: What the preference is about. E.g., "verbosity", "tone", "max_length".
    value: The preference value. E.g., "concise", "formal", "500".
    source: How it was learned. "explicit" (user said it), "implicit" (inferred
            from feedback patterns), "graduated" (promoted from another project).
    priority: 0-100. Higher = stronger preference. Explicit > implicit.
    """

    preference_type: str
    key: str
    value: str
    project_id: str = "default"
    source: str = "implicit"
    priority: int = 50
    active: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:12])
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())


# =============================================================================
# AGENT TRUST SCORE
# =============================================================================


@dataclass
class AgentTrustScore:
    """
    Trust score for an agent -- updated by feedback signals.

    trust_score: 0.0 (no trust) to 1.0 (full trust). Default 0.5 (neutral).
    interaction_count: How many interactions have been scored.
    acceptance_rate: Rolling acceptance rate from recent signals.
    """

    agent_id: str
    project_id: str = "default"
    trust_score: float = 0.5
    interaction_count: int = 0
    acceptance_rate: float = 0.5
    last_signal_type: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())


# =============================================================================
# CHECK-IN
# =============================================================================


@dataclass
class CheckIn:
    """
    Permission prompt -- asks the user before adapting behavior.

    The system never adapts silently. When it detects a pattern worth acting on,
    it creates a CheckIn and waits for the user to approve, reject, or skip.

    checkin_type: What triggered this. E.g., "threshold" (N signals reached),
                  "time" (periodic), "drift" (preference changed), "milestone".
    prompt: Human-readable question to show the user.
    suggested_action: What the system wants to do if approved.
    """

    checkin_type: str
    prompt: str
    suggested_action: str = ""
    project_id: str = "default"
    status: str = CheckInStatus.PENDING
    response: str = ""
    context: dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:12])
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    expires_at: str = ""
    resolved_at: str = ""
