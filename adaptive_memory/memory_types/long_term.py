"""
Long-term Memory implementation.
Manages permanent user profile preferences, domain constraints, and durable knowledge.
Operates with high default confidence and indefinite retention without automated expiration.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from adaptive_memory.models import MemoryRecord, MemoryStatus, MemoryType, SafetyTier


class LongTermMemory:
    """
    Handler for permanent, durable knowledge records.
    Attributes:
        auto_expires: False
        promotable: False (Already permanent)
    """
    auto_expires: bool = False
    promotable: bool = False

    @classmethod
    def create_record(
        cls,
        user_id: str,
        content: str,
        task_context: Optional[str] = None,
        source: str = "user",
        confidence: float = 0.85,
        importance: float = 0.8,
        risk_level: SafetyTier = SafetyTier.T1_PERSONAL,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> MemoryRecord:
        """Create a new durable long-term record."""
        now = datetime.now(timezone.utc)
        return MemoryRecord(
            user_id=user_id,
            content=content.strip(),
            memory_type=MemoryType.LONG_TERM,
            created_at=now,
            updated_at=now,
            expires_at=None,  # Permanent
            source=source,
            task_context=task_context,
            confidence=confidence,
            utility=0.7,
            importance=importance,
            recency=1.0,
            risk_level=risk_level,
            status=MemoryStatus.ACTIVE,
            metadata=metadata or {},
        )

    @classmethod
    def update_preference(
        cls,
        record: MemoryRecord,
        new_content: str,
        confidence: Optional[float] = None,
        metadata_patch: Optional[Dict[str, Any]] = None,
    ) -> MemoryRecord:
        """Explicitly update permanent preference or constraint content."""
        if record.memory_type != MemoryType.LONG_TERM:
            raise ValueError(f"Record {record.id} is not a long-term memory")

        now = datetime.now(timezone.utc)
        updated = record.model_copy(deep=True)
        updated.content = new_content.strip()
        updated.updated_at = now
        if confidence is not None:
            updated.confidence = max(0.0, min(1.0, confidence))
        if metadata_patch:
            updated.metadata.update(metadata_patch)
        updated.metadata["previous_version"] = record.content
        return updated
