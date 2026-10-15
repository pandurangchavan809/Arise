"""
Prospective Memory implementation.
Manages future intentions, scheduled reminders, and event-conditioned triggers.
Tracks lifecycle states: PENDING, TRIGGERED, PRESENTED, COMPLETED, ARCHIVED.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
import structlog

from adaptive_memory.models import MemoryRecord, MemoryStatus, MemoryType, SafetyTier

logger = structlog.get_logger(__name__)


class ProspectiveState(str, Enum):
    """Lifecycle state of a prospective intention/reminder."""
    PENDING = "pending"
    TRIGGERED = "triggered"
    PRESENTED = "presented"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class ProspectiveMemory:
    """
    Handler for prospective memory triggers, reminders, and future intents.
    """
    auto_expires: bool = False
    promotable: bool = False

    @classmethod
    def create_record(
        cls,
        user_id: str,
        content: str,
        trigger_time: Optional[datetime] = None,
        trigger_condition: Optional[str] = None,
        task_context: Optional[str] = None,
        confidence: float = 0.9,
        importance: float = 0.8,
        risk_level: SafetyTier = SafetyTier.T1_PERSONAL,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> MemoryRecord:
        """Create a prospective memory record with trigger criteria."""
        now = datetime.now(timezone.utc)
        meta = metadata or {}
        meta["prospective_state"] = ProspectiveState.PENDING.value
        meta["trigger_condition"] = trigger_condition
        meta["trigger_time"] = trigger_time.isoformat() if trigger_time else None

        return MemoryRecord(
            user_id=user_id,
            content=content.strip(),
            memory_type=MemoryType.PROSPECTIVE,
            created_at=now,
            updated_at=now,
            expires_at=None,
            source="reminder",
            task_context=task_context,
            confidence=confidence,
            utility=0.8,
            importance=importance,
            recency=1.0,
            risk_level=risk_level,
            status=MemoryStatus.ACTIVE,
            metadata=meta,
        )

    @classmethod
    def evaluate_trigger(
        cls,
        record: MemoryRecord,
        current_time: Optional[datetime] = None,
        current_context: Optional[str] = None,
        event_name: Optional[str] = None,
    ) -> bool:
        """
        Evaluate if a prospective memory's trigger conditions are met.
        Conditions can be temporal (trigger_time), contextual (keyword match), or event-based.
        """
        if record.memory_type != MemoryType.PROSPECTIVE:
            return False

        current_state = record.metadata.get("prospective_state", ProspectiveState.PENDING.value)
        if current_state != ProspectiveState.PENDING.value:
            return False

        now = current_time or datetime.now(timezone.utc)

        # Temporal trigger evaluation
        trigger_time_str = record.metadata.get("trigger_time")
        if trigger_time_str:
            trigger_time = datetime.fromisoformat(trigger_time_str)
            if trigger_time.tzinfo is None:
                trigger_time = trigger_time.replace(tzinfo=timezone.utc)
            if now >= trigger_time:
                return True

        # Context/event condition evaluation
        cond = record.metadata.get("trigger_condition")
        if cond:
            cond_lower = cond.lower()
            if event_name and event_name.lower() in cond_lower:
                return True
            if current_context and cond_lower in current_context.lower():
                return True

        return False

    @classmethod
    def transition_state(
        cls,
        record: MemoryRecord,
        new_state: ProspectiveState,
    ) -> MemoryRecord:
        """Advance prospective memory state."""
        if record.memory_type != MemoryType.PROSPECTIVE:
            raise ValueError(f"Record {record.id} is not a prospective memory")

        now = datetime.now(timezone.utc)
        updated = record.model_copy(deep=True)
        updated.updated_at = now
        updated.metadata["prospective_state"] = new_state.value
        updated.metadata[f"state_changed_to_{new_state.value}_at"] = now.isoformat()

        if new_state in (ProspectiveState.COMPLETED, ProspectiveState.ARCHIVED):
            updated.status = MemoryStatus.ARCHIVED

        logger.debug("Prospective state transitioned", memory_id=record.id, new_state=new_state.value)
        return updated

    @classmethod
    def mark_triggered(cls, record: MemoryRecord) -> MemoryRecord:
        """Convenience method to transition state to TRIGGERED."""
        return cls.transition_state(record, ProspectiveState.TRIGGERED)

    @classmethod
    def mark_completed(cls, record: MemoryRecord) -> MemoryRecord:
        """Convenience method to transition state to COMPLETED."""
        return cls.transition_state(record, ProspectiveState.COMPLETED)
