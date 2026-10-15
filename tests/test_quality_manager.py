"""
Unit tests for Memory Quality Manager, Scoring, and Budget Control.
"""

import asyncio
from datetime import datetime, timezone
import pytest

from adaptive_memory.core.budget import EdgeBudgetController
from adaptive_memory.core.conflicts import ConflictDetector
from adaptive_memory.core.manager import MemoryQualityManager
from adaptive_memory.core.quality import QualityScorer
from adaptive_memory.models import (
    DecisionType,
    EdgeBudget,
    MemoryRecord,
    MemoryStatus,
    MemoryType,
    OutcomeType,
    SafetyTier,
)
from adaptive_memory.storage.sqlite import SQLiteStorage


@pytest.mark.asyncio
async def test_quality_scorer_formula():
    scorer = QualityScorer()
    record = MemoryRecord(
        user_id="test_user",
        content="I prefer dark mode in all editors",
        confidence=0.8,
        utility=0.6,
        importance=0.7,
        risk_level=SafetyTier.T1_PERSONAL,
    )
    score = scorer.score(record, query="dark mode editors")
    assert score.relevance > 0.0
    assert score.utility == 0.6
    assert score.total > 0.0
    assert "formula" in score.explanation


@pytest.mark.asyncio
async def test_memory_storage_and_recall():
    storage = SQLiteStorage(database_url="sqlite:///:memory:")
    await storage.initialize()

    manager = MemoryQualityManager(storage=storage)

    # Store memory
    rec = await manager.remember(
        content="User lives in San Francisco, CA",
        user_id="user_123",
        memory_type=MemoryType.LONG_TERM,
        confidence=0.9,
        risk_level=SafetyTier.T1_PERSONAL,
    )
    assert rec.id is not None

    # Recall
    recall_res = await manager.recall(query="where does user live?", user_id="user_123")
    assert len(recall_res.selected) == 1
    assert recall_res.selected[0].memory.id == rec.id

    # Outcome feedback update: helpful
    await manager.record_outcome([rec.id], OutcomeType.HELPFUL, "user_123")
    updated = await storage.get(rec.id)
    assert updated.utility > 0.5  # 0.7 * 0.5 + 0.3 * 1.0 = 0.65

    await storage.close()


@pytest.mark.asyncio
async def test_safety_tier_cannot_be_suppressed_by_lower_tier():
    storage = SQLiteStorage(database_url="sqlite:///:memory:")
    await storage.initialize()
    manager = MemoryQualityManager(storage=storage)

    # Budget limit = 1 memory
    budget = EdgeBudget(max_memories=1, max_context_tokens=500)

    # Insert a casual low-risk memory
    low_tier = await manager.remember(
        content="Casual preference: coffee in morning",
        user_id="user_abc",
        memory_type=MemoryType.SESSION,
        confidence=0.9,
        risk_level=SafetyTier.T0_CASUAL,
    )

    # Insert a critical operational safety memory
    high_tier = await manager.remember(
        content="Critical constraint: NEVER deploy to production without approval",
        user_id="user_abc",
        memory_type=MemoryType.LONG_TERM,
        confidence=0.95,
        risk_level=SafetyTier.T2_OPERATIONAL,
    )

    res = await manager.recall(
        query="coffee or deploy rules",
        user_id="user_abc",
        budget=budget,
    )

    # High tier MUST be selected over low tier when budget is limited to 1
    assert len(res.selected) == 1
    assert res.selected[0].memory.id == high_tier.id
    assert res.selected[0].memory.risk_level >= SafetyTier.T2_OPERATIONAL

    await storage.close()


@pytest.mark.asyncio
async def test_conflict_detection_and_resolution():
    detector = ConflictDetector()

    now = datetime.now(timezone.utc)
    old_mem = MemoryRecord(
        id="mem_old",
        user_id="user_xyz",
        content="User resides in Seattle Washington",
        created_at=now,
        updated_at=now,
        confidence=0.7,
        source="user",
    )
    new_mem = MemoryRecord(
        id="mem_new",
        user_id="user_xyz",
        content="User resides in London United Kingdom",
        created_at=now,
        updated_at=now,
        confidence=0.85,
        source="user",
    )

    conflicts = detector.detect([old_mem, new_mem])
    assert len(conflicts) >= 1
    assert conflicts[0].resolution_id == "mem_new"
