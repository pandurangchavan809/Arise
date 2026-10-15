"""
Session Memory implementation.
Manages ephemeral, interaction-scoped memories with automated TTL expiration
and promotion capabilities to permanent long-term memory.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from adaptive_memory.models import MemoryRecord, MemoryStatus, MemoryType, SafetyTier


class SessionMemory:
    """
    Handler for ephemeral session-scoped memory.
    Attributes:
        DEFAULT_TTL_SECONDS: Default time-to-live for a session record (1 hour).
        auto_expires: True
        promotable: True
    """
    DEFAULT_TTL_SECONDS = 3600
    auto_expires: bool = True
    promotable: bool = True

    @classmethod
    def create_record(
        cls,
        user_id: str,
        content: str,
        session_id: str,
        ttl_seconds: int = DEFAULT_TTL_SECONDS,
        task_context: Optional[str] = None,
        confidence: float = 0.6,
        importance: float = 0.4,
        risk_level: SafetyTier = SafetyTier.T0_CASUAL,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> MemoryRecord:
        """Create a new session-scoped memory record with expiry."""
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(seconds=ttl_seconds)

        meta = metadata or {}
        meta["session_id"] = session_id

        return MemoryRecord(
            user_id=user_id,
            content=content.strip(),
            memory_type=MemoryType.SESSION,
            created_at=now,
            updated_at=now,
            expires_at=expires_at,
            source="session",
            task_context=task_context or f"session:{session_id}",
            confidence=confidence,
            utility=0.5,
            importance=importance,
            recency=1.0,
            risk_level=risk_level,
            status=MemoryStatus.ACTIVE,
            metadata=meta,
        )

    @classmethod
    def is_expired(cls, record: MemoryRecord) -> bool:
        """Evaluate if the session record has exceeded its expiration timestamp."""
        if not record.expires_at:
            return False
        now = datetime.now(timezone.utc)
        exp = record.expires_at
        if exp.tzinfo is None:
            exp = exp.replace(tzinfo=timezone.utc)
        return now >= exp

    @classmethod
    def promote_to_long_term(cls, record: MemoryRecord) -> MemoryRecord:
        """Prepare record representation for permanent elevation to LONG_TERM."""
        if record.memory_type != MemoryType.SESSION:
            raise ValueError(f"Cannot promote non-session record {record.id}")

        now = datetime.now(timezone.utc)
        updated = record.model_copy(deep=True)
        updated.memory_type = MemoryType.LONG_TERM
        updated.expires_at = None
        updated.updated_at = now
        updated.confidence = min(record.confidence + 0.15, 1.0)
        updated.metadata["promoted_from_session_at"] = now.isoformat()
        return updated
