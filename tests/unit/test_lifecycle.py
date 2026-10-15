"""
Unit tests for MemoryLifecycle: expiration checks, promotions, status transitions, and session cleanups.
"""

from datetime import datetime, timedelta, timezone
import pytest

from adaptive_memory.core.lifecycle import MemoryLifecycle
from adaptive_memory.models import MemoryRecord, MemoryStatus, MemoryType, SafetyTier
from adaptive_memory.storage.sqlite import SQLiteStorage


@pytest.mark.asyncio
async def test_session_memory_expiration(storage: SQLiteStorage):
    """Test that check_expirations identifies and marks expired session memories."""
    now = datetime.now(timezone.utc)
    expired_mem = MemoryRecord(
        user_id="user_expire",
        content="Temporary session token abc-123",
        memory_type=MemoryType.SESSION,
        status=MemoryStatus.ACTIVE,
        expires_at=now - timedelta(minutes=10),
    )
    future_mem = MemoryRecord(
        user_id="user_expire",
        content="Future session token xyz-789",
        memory_type=MemoryType.SESSION,
        status=MemoryStatus.ACTIVE,
        expires_at=now + timedelta(hours=1),
    )

    await storage.store(expired_mem)
    await storage.store(future_mem)

    transitioned = await MemoryLifecycle.check_expirations(storage)

    assert expired_mem.id in transitioned
    assert future_mem.id not in transitioned

    # Verify status in database
    rec_expired = await storage.get(expired_mem.id)
    assert rec_expired.status == MemoryStatus.EXPIRED

    rec_future = await storage.get(future_mem.id)
    assert rec_future.status == MemoryStatus.ACTIVE


@pytest.mark.asyncio
async def test_memory_promotion(storage: SQLiteStorage):
    """Test promoting a SESSION memory to LONG_TERM, elevating confidence and clearing expiry."""
    now = datetime.now(timezone.utc)
    mem = MemoryRecord(
        user_id="user_promo",
        content="User frequently works with TypeScript and Next.js",
        memory_type=MemoryType.SESSION,
        confidence=0.6,
        status=MemoryStatus.ACTIVE,
        expires_at=now + timedelta(hours=2),
    )
    stored = await storage.store(mem)

    promoted = await MemoryLifecycle.promote(
        memory_id=stored.id,
        new_type=MemoryType.LONG_TERM,
        storage=storage,
        elevate_confidence=0.15,
    )

    assert promoted.memory_type == MemoryType.LONG_TERM
    assert promoted.confidence == 0.75
    assert promoted.expires_at is None


@pytest.mark.asyncio
async def test_status_transitions(storage: SQLiteStorage):
    """Test transitioning memory statuses through ACTIVE -> ARCHIVED -> SUPPRESSED."""
    mem = MemoryRecord(
        user_id="user_status",
        content="Outdated infrastructure configuration flag",
        memory_type=MemoryType.EXPERIENCE,
        status=MemoryStatus.ACTIVE,
    )
    stored = await storage.store(mem)

    archived = await MemoryLifecycle.update_status(
        memory_id=stored.id,
        status=MemoryStatus.ARCHIVED,
        storage=storage,
    )
    assert archived.status == MemoryStatus.ARCHIVED

    suppressed = await MemoryLifecycle.update_status(
        memory_id=stored.id,
        status=MemoryStatus.SUPPRESSED,
        storage=storage,
    )
    assert suppressed.status == MemoryStatus.SUPPRESSED


@pytest.mark.asyncio
async def test_cleanup_session(storage: SQLiteStorage):
    """Test cleanup_session archives all memories tied to a completed session."""
    session_id = "session_build_99"
    now = datetime.now(timezone.utc)

    mem1 = MemoryRecord(
        user_id="user_cleanup",
        content="Session intermediate compile state 1",
        memory_type=MemoryType.SESSION,
        status=MemoryStatus.ACTIVE,
        task_context=session_id,
        metadata={"session_id": session_id},
    )
    mem2 = MemoryRecord(
        user_id="user_cleanup",
        content="Session intermediate compile state 2",
        memory_type=MemoryType.SESSION,
        status=MemoryStatus.ACTIVE,
        task_context=session_id,
        metadata={"session_id": session_id},
    )
    mem3 = MemoryRecord(
        user_id="user_cleanup",
        content="Unrelated persistent memory",
        memory_type=MemoryType.LONG_TERM,
        status=MemoryStatus.ACTIVE,
        task_context="other_context",
    )

    await storage.store(mem1)
    await storage.store(mem2)
    await storage.store(mem3)

    count = await MemoryLifecycle.cleanup_session(session_id, storage)
    assert count == 2

    r1 = await storage.get(mem1.id)
    r2 = await storage.get(mem2.id)
    r3 = await storage.get(mem3.id)

    assert r1.status == MemoryStatus.ARCHIVED
    assert r2.status == MemoryStatus.ARCHIVED
    assert r3.status == MemoryStatus.ACTIVE


@pytest.mark.asyncio
async def test_prospective_lifecycle_states(storage: SQLiteStorage):
    """Test prospective task memory lifecycle: ACTIVE -> ARCHIVED after completion."""
    task_mem = MemoryRecord(
        user_id="user_prosp",
        content="Send notification email after batch index completes",
        memory_type=MemoryType.PROSPECTIVE,
        confidence=0.9,
        risk_level=SafetyTier.T2_OPERATIONAL,
        status=MemoryStatus.ACTIVE,
    )
    stored = await storage.store(task_mem)
    assert stored.status == MemoryStatus.ACTIVE

    # Mark prospective task completed
    completed = await MemoryLifecycle.update_status(
        memory_id=stored.id,
        status=MemoryStatus.ARCHIVED,
        storage=storage,
    )
    assert completed.status == MemoryStatus.ARCHIVED
