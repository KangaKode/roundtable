"""
Learning system database schema -- SQLite tables for feedback, preferences, trust, check-ins.

Usage:
    initialize_schema(db_path)  # Creates tables if they don't exist
    get_connection(db_path)     # Returns a connection with WAL mode enabled

All tables use TEXT primary keys (UUIDs) and TEXT timestamps (ISO format).
JSON fields store arbitrary metadata as serialized strings.

Keep this file under 150 lines.
"""

import json
import logging
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

DEFAULT_DB_PATH = Path("data/learning.db")

SCHEMA_SQL = """
-- Feedback signals: atomic user reactions to agent outputs
CREATE TABLE IF NOT EXISTS feedback_signals (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL DEFAULT 'default',
    signal_type TEXT NOT NULL,
    context_type TEXT DEFAULT '',
    agent_id TEXT DEFAULT '',
    content TEXT DEFAULT '',
    confidence REAL DEFAULT 0.5,
    metadata_json TEXT DEFAULT '{}',
    session_id TEXT DEFAULT '',
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_feedback_project
    ON feedback_signals(project_id, created_at);
CREATE INDEX IF NOT EXISTS idx_feedback_agent
    ON feedback_signals(agent_id, signal_type);
CREATE INDEX IF NOT EXISTS idx_feedback_context
    ON feedback_signals(context_type, created_at);

-- User preferences: learned key-value pairs with priority and source
CREATE TABLE IF NOT EXISTS user_preferences (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL DEFAULT 'default',
    preference_type TEXT NOT NULL,
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    source TEXT DEFAULT 'implicit',
    priority INTEGER DEFAULT 50,
    active INTEGER DEFAULT 1,
    metadata_json TEXT DEFAULT '{}',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_prefs_project
    ON user_preferences(project_id, active);
CREATE INDEX IF NOT EXISTS idx_prefs_type
    ON user_preferences(preference_type, key);

-- Agent trust scores: EMA-based trust per agent
CREATE TABLE IF NOT EXISTS agent_trust (
    agent_id TEXT NOT NULL,
    project_id TEXT NOT NULL DEFAULT 'default',
    trust_score REAL DEFAULT 0.5,
    interaction_count INTEGER DEFAULT 0,
    acceptance_rate REAL DEFAULT 0.5,
    last_signal_type TEXT DEFAULT '',
    metadata_json TEXT DEFAULT '{}',
    last_updated TEXT NOT NULL,
    PRIMARY KEY (project_id, agent_id)
);

-- Check-ins: permission prompts for adaptation
CREATE TABLE IF NOT EXISTS checkins (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL DEFAULT 'default',
    checkin_type TEXT NOT NULL,
    prompt TEXT NOT NULL,
    suggested_action TEXT DEFAULT '',
    status TEXT DEFAULT 'pending',
    response TEXT DEFAULT '',
    context_json TEXT DEFAULT '{}',
    created_at TEXT NOT NULL,
    expires_at TEXT DEFAULT '',
    resolved_at TEXT DEFAULT ''
);

CREATE INDEX IF NOT EXISTS idx_checkins_status
    ON checkins(project_id, status);
"""


def get_connection(db_path: Path = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """Get a SQLite connection with WAL mode and foreign keys enabled."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.row_factory = sqlite3.Row
    return conn


def initialize_schema(db_path: Path = DEFAULT_DB_PATH) -> None:
    """Create learning system tables if they don't exist."""
    conn = get_connection(db_path)
    try:
        conn.executescript(SCHEMA_SQL)
        conn.commit()
        logger.info(f"[LearningSchema] Initialized at {db_path}")
    finally:
        conn.close()


def dict_from_row(row: sqlite3.Row) -> dict:
    """Convert a sqlite3.Row to a plain dict, parsing JSON fields."""
    d = dict(row)
    for key in list(d.keys()):
        if key.endswith("_json") and isinstance(d[key], str):
            try:
                d[key.replace("_json", "")] = json.loads(d[key])
                del d[key]
            except json.JSONDecodeError:
                d[key.replace("_json", "")] = {}
                del d[key]
    return d
