"""
Lifecycle management for memory records.
Handles background expiration checks, tier promotion, status transitions,
and session cleanup routines.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional
import structlog

from adaptive_memory.models import MemoryRecord, MemoryStatus, MemoryType

if TYPE_CHECKING:
    from adaptive_memory.storage.interface import StorageBackend

logger = structlog.get_logger(__name__)


class MemoryLifecycle:
    """
    Manages automated and explicit state changes for memories throughout their lifecycle.
    """

    @staticmethod
    async def check_expirations(storage: StorageBackend) -> List[str]:
        """
        Scan and transition expired memories to ARCHIVED or EXPIRED status.
        Returns list of transitioned memory IDs.
        """
        now = datetime.now(timezone.utc)
        expired_records = await storage.get_expired(before=now)
        transitioned_ids: List[str] = []

        for record in expired_records:
            if record.status == MemoryStatus.ACTIVE:
                await storage.update(
                    record.id,
                    {
                        "status": MemoryStatus.EXPIRED.value,
                        "updated_at": now.isoformat(),
                    }
                )
                transitioned_ids.append(record.id)
                logger.info("Memory expired and marked EXPIRED", memory_id=record.id)

        return transitioned_ids

    @staticmethod
    async def promote(
        memory_id: str,
        new_type: MemoryType,
        storage: StorageBackend,
        elevate_confidence: float = 0.1,
    ) -> MemoryRecord:
        """
        Promote a memory (e.g. from SESSION to LONG_TERM).
        Updates memory_type, adjusts confidence, and removes auto-expiry if moving to long_term.
        """
        record = await storage.get(memory_id)
        if not record:
            raise ValueError(f"Memory with ID {memory_id} not found")

        updates: dict = {
            "memory_type": new_type.value,
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "confidence": min(record.confidence + elevate_confidence, 1.0),
        }

        # Clear expiration when promoted to permanent/long_term
        if new_type == MemoryType.LONG_TERM:
            updates["expires_at"] = None

        updated_record = await storage.update(memory_id, updates)
        logger.info(
            "Memory promoted",
            memory_id=memory_id,
            previous_type=record.memory_type.value,
            new_type=new_type.value,
        )
        return updated_record

    @staticmethod
    async def update_status(
        memory_id: str,
        status: MemoryStatus,
        storage: StorageBackend,
    ) -> MemoryRecord:
        """Transition memory to a target status (e.g., ACTIVE -> ARCHIVED / SUPPRESSED)."""
        record = await storage.get(memory_id)
        if not record:
            raise ValueError(f"Memory with ID {memory_id} not found")

        updated_record = await storage.update(
            memory_id,
            {
                "status": status.value,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
        )
        logger.info("Memory status updated", memory_id=memory_id, new_status=status.value)
        return updated_record

    @staticmethod
    async def cleanup_session(session_id: str, storage: StorageBackend) -> int:
        """
        Clean up or archive temporary memories associated with a terminated session.
        Returns the count of archived session memories.
        """
        # Look up records tagged with session_id in task_context or metadata
        # We query session memories and filter by matching session identifier
        session_records = await storage.search(
            query=session_id,
            user_id="",  # or across user if session matches
            memory_types=[MemoryType.SESSION],
            limit=200,
        )
        archived_count = 0
        now = datetime.now(timezone.utc)

        for record in session_records:
            is_match = (
                record.task_context == session_id
                or record.metadata.get("session_id") == session_id
            )
            if is_match and record.status == MemoryStatus.ACTIVE:
                await storage.update(
                    record.id,
                    {
                        "status": MemoryStatus.ARCHIVED.value,
                        "updated_at": now.isoformat(),
                    }
                )
                archived_count += 1

        logger.info("Session cleanup finished", session_id=session_id, archived_count=archived_count)
        return archived_count
