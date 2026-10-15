"""
Unit tests for MemoryQualityManager: ingestion, recall pipeline, outcome calibration, and lifecycle management.
"""

import pytest

from adaptive_memory.core.manager import MemoryQualityManager
from adaptive_memory.models import (
    MemoryRecord,
    MemoryStatus,
    MemoryType,
    OutcomeType,
    RecallResult,
    SafetyTier,
)
from adaptive_memory.storage.sqlite import SQLiteStorage


@pytest.mark.asyncio
async def test_remember_creates_memory(manager: MemoryQualityManager, storage: SQLiteStorage):
    """Test storing a new memory record via MemoryQualityManager.remember."""
    rec = await manager.remember(
        content="Primary cloud deployment uses AWS us-west-2 region",
        user_id="user_mgr",
        memory_type=MemoryType.LONG_TERM,
        confidence=0.85,
        importance=0.9,
        risk_level=SafetyTier.T2_OPERATIONAL,
        task_context="infra_setup",
    )

    assert rec is not None
    assert rec.id is not None
    assert rec.user_id == "user_mgr"
    assert rec.content == "Primary cloud deployment uses AWS us-west-2 region"
    assert rec.memory_type == MemoryType.LONG_TERM
    assert rec.confidence == 0.85
    assert rec.importance == 0.9
    assert rec.risk_level == SafetyTier.T2_OPERATIONAL
    assert rec.status == MemoryStatus.ACTIVE

    # Verify retrieval from storage
    stored = await storage.get(rec.id)
    assert stored is not None
    assert stored.id == rec.id


@pytest.mark.asyncio
async def test_recall_returns_results(manager: MemoryQualityManager):
    """Test that recall retrieves relevant stored memories matching query terms."""
    await manager.remember(
        content="Configured Redis cache with 30-minute TTL",
        user_id="user_recall",
        memory_type=MemoryType.LONG_TERM,
    )
    await manager.remember(
        content="PostgreSQL database connection pool size set to 20",
        user_id="user_recall",
        memory_type=MemoryType.LONG_TERM,
    )

    result: RecallResult = await manager.recall(
        query="Redis cache TTL",
        user_id="user_recall",
    )

    assert result is not None
    assert len(result.selected) >= 1
    contents = [c.memory.content for c in result.selected]
    assert any("Redis cache" in c for c in contents)


@pytest.mark.asyncio
async def test_recall_applies_quality_scoring(manager: MemoryQualityManager):
    """Test that recall applies quality scores and explanation traces to candidates."""
    await manager.remember(
        content="Python asyncio event loop guidelines and best practices",
        user_id="user_qs",
        memory_type=MemoryType.EXPERIENCE,
        confidence=0.9,
    )

    result = await manager.recall(query="Python asyncio guidelines", user_id="user_qs")

    assert len(result.selected) >= 1
    first_candidate = result.selected[0]
    assert first_candidate.score is not None
    assert first_candidate.score.total > 0.0
    assert first_candidate.score.relevance > 0.0
    assert first_candidate.decision is not None
    assert first_candidate.decision.decision.value == "included"


@pytest.mark.asyncio
async def test_outcome_updates_utility_helpful(manager: MemoryQualityManager, storage: SQLiteStorage):
    """Test that HELPFUL feedback increases memory utility score."""
    rec = await manager.remember(
        content="Kubernetes rolling deployment rollback command",
        user_id="user_outcome",
    )
    initial_utility = rec.utility  # 0.5 default

    await manager.record_outcome(
        memory_ids=[rec.id],
        outcome=OutcomeType.HELPFUL,
        user_id="user_outcome",
    )

    updated = await storage.get(rec.id)
    assert updated is not None
    # target_utility is 1.0 -> new_utility = 0.7 * 0.5 + 0.3 * 1.0 = 0.65
    assert updated.utility > initial_utility
    assert updated.utility == pytest.approx(0.65, abs=0.01)


@pytest.mark.asyncio
async def test_outcome_updates_utility_misleading(manager: MemoryQualityManager, storage: SQLiteStorage):
    """Test that MISLEADING feedback decreases memory utility score."""
    rec = await manager.remember(
        content="Outdated API endpoint /v1/auth/token deprecated",
        user_id="user_mislead",
    )
    initial_utility = rec.utility  # 0.5 default

    await manager.record_outcome(
        memory_ids=[rec.id],
        outcome=OutcomeType.MISLEADING,
        user_id="user_mislead",
    )

    updated = await storage.get(rec.id)
    assert updated is not None
    # target_utility is 0.0 -> new_utility = 0.7 * 0.5 + 0.3 * 0.0 = 0.35
    assert updated.utility < initial_utility
    assert updated.utility == pytest.approx(0.35, abs=0.01)


@pytest.mark.asyncio
async def test_forget_sets_status(manager: MemoryQualityManager, storage: SQLiteStorage):
    """Test that forget removes the memory from active storage."""
    rec = await manager.remember(
        content="Temporary secret token to be discarded",
        user_id="user_forget",
    )

    forgotten = await manager.forget(memory_id=rec.id, user_id="user_forget")
    assert forgotten is True

    # Memory should no longer exist in storage
    record_in_storage = await storage.get(rec.id)
    assert record_in_storage is None


@pytest.mark.asyncio
async def test_archive_sets_status(manager: MemoryQualityManager, storage: SQLiteStorage):
    """Test that archive updates memory status to ARCHIVED while preserving it in storage."""
    rec = await manager.remember(
        content="Completed Q3 milestone architecture specifications",
        user_id="user_archive",
    )

    archived = await manager.archive(memory_id=rec.id, user_id="user_archive")
    assert archived.status == MemoryStatus.ARCHIVED

    stored = await storage.get(rec.id)
    assert stored is not None
    assert stored.status == MemoryStatus.ARCHIVED
