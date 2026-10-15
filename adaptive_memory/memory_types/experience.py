"""
Experience Memory implementation.
Captures agent execution episodes, tool results, and procedural problem-solving patterns.
Utility is continuously updated via outcome signals, down-ranking repeated failures.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from adaptive_memory.models import MemoryRecord, MemoryStatus, MemoryType, SafetyTier


class ExperienceMemory:
    """
    Handler for experiential records representing problem-solving attempts and tool results.
    """
    auto_expires: bool = False
    promotable: bool = False

    @classmethod
    def create_record(
        cls,
        user_id: str,
        content: str,
        task_context: str,
        success: bool = True,
        utility: float = 0.6,
        confidence: float = 0.7,
        importance: float = 0.5,
        risk_level: SafetyTier = SafetyTier.T1_PERSONAL,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> MemoryRecord:
        """Create a new experience memory record tracking an execution outcome."""
        now = datetime.now(timezone.utc)
        meta = metadata or {}
        meta.setdefault("success_count", 1 if success else 0)
        meta.setdefault("failure_count", 0 if success else 1)
        meta.setdefault("total_runs", 1)

        initial_utility = utility if success else max(utility - 0.3, 0.1)

        return MemoryRecord(
            user_id=user_id,
            content=content.strip(),
            memory_type=MemoryType.EXPERIENCE,
            created_at=now,
            updated_at=now,
            expires_at=None,
            source="experience",
            task_context=task_context,
            confidence=confidence,
            utility=round(initial_utility, 3),
            importance=importance,
            recency=1.0,
            risk_level=risk_level,
            status=MemoryStatus.ACTIVE,
            metadata=meta,
        )

    @classmethod
    def record_feedback(
        cls,
        record: MemoryRecord,
        success: bool,
        notes: Optional[str] = None,
    ) -> MemoryRecord:
        """
        Record a subsequent execution trial outcome.
        Down-ranks utility on repeated failures or reinforces utility on success.
        """
        if record.memory_type != MemoryType.EXPERIENCE:
            raise ValueError(f"Record {record.id} is not an experience memory")

        now = datetime.now(timezone.utc)
        updated = record.model_copy(deep=True)
        updated.updated_at = now

        meta = updated.metadata
        total_runs = meta.get("total_runs", 1) + 1
        meta["total_runs"] = total_runs

        if success:
            meta["success_count"] = meta.get("success_count", 0) + 1
            # Reinforce utility
            updated.utility = min(1.0, round(updated.utility * 0.7 + 0.3 * 1.0, 3))
            updated.confidence = min(1.0, round(updated.confidence + 0.05, 3))
        else:
            meta["failure_count"] = meta.get("failure_count", 0) + 1
            # Penalize utility on failure
            updated.utility = max(0.05, round(updated.utility * 0.6, 3))
            updated.confidence = max(0.1, round(updated.confidence - 0.1, 3))

        if notes:
            trials = meta.setdefault("trials", [])
            trials.append({"timestamp": now.isoformat(), "success": success, "notes": notes})

        return updated

    @classmethod
    def record_success(cls, record: MemoryRecord, notes: Optional[str] = None) -> MemoryRecord:
        """Record successful outcome trial."""
        return cls.record_feedback(record, success=True, notes=notes)

    @classmethod
    def record_failure(cls, record: MemoryRecord, notes: Optional[str] = None) -> MemoryRecord:
        """Record failed outcome trial."""
        return cls.record_feedback(record, success=False, notes=notes)
