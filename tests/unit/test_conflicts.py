"""
Unit tests for ConflictDetector: pairwise conflict detection and deterministic resolution rules.
"""

from datetime import datetime, timedelta, timezone
import pytest

from adaptive_memory.core.conflicts import ConflictDetector, ConflictGroup
from adaptive_memory.models import MemoryRecord, MemoryType, SafetyTier


@pytest.fixture
def detector() -> ConflictDetector:
    return ConflictDetector(keyword_overlap_threshold=0.6)


def test_no_conflicts(detector: ConflictDetector):
    """Test that orthogonal, non-overlapping memories produce no detected conflict groups."""
    mem1 = MemoryRecord(
        user_id="user_1",
        content="User preferred programming language is Python",
        memory_type=MemoryType.LONG_TERM,
    )
    mem2 = MemoryRecord(
        user_id="user_1",
        content="Primary staging database is PostgreSQL version 16",
        memory_type=MemoryType.LONG_TERM,
    )

    conflicts = detector.detect([mem1, mem2])
    assert conflicts == []


def test_temporal_conflict_resolution(detector: ConflictDetector):
    """Test that between equivalent memories, the more recently updated memory wins."""
    now = datetime.now(timezone.utc)
    mem_old = MemoryRecord(
        id="mem_old",
        user_id="user_1",
        content="Current active development branch is feature-auth-v1",
        confidence=0.8,
        source="user",
        created_at=now - timedelta(days=2),
        updated_at=now - timedelta(days=2),
    )
    mem_new = MemoryRecord(
        id="mem_new",
        user_id="user_1",
        content="Current active development branch is feature-auth-v2",
        confidence=0.8,
        source="user",
        created_at=now - timedelta(hours=1),
        updated_at=now - timedelta(hours=1),
    )

    conflicts = detector.detect([mem_old, mem_new])
    assert len(conflicts) == 1
    assert conflicts[0].resolution_id == "mem_new"
    assert "Newer memory" in conflicts[0].reason


def test_explicit_overrides_implicit(detector: ConflictDetector):
    """Test that explicit user instruction overrides an inferred agent observation."""
    now = datetime.now(timezone.utc)
    mem_agent = MemoryRecord(
        id="mem_agent",
        user_id="user_1",
        content="User preferred theme setting is dark mode",
        source="agent",  # implicit deduction
        confidence=0.9,
        created_at=now,
        updated_at=now,
    )
    mem_user = MemoryRecord(
        id="mem_user",
        user_id="user_1",
        content="User preferred theme setting is light mode high contrast",
        source="user",  # explicit user statement
        confidence=0.85,
        created_at=now - timedelta(hours=1),
        updated_at=now - timedelta(hours=1),
    )

    conflicts = detector.detect([mem_agent, mem_user])
    assert len(conflicts) == 1
    assert conflicts[0].resolution_id == "mem_user"
    assert "Explicit user origin supersedes" in conflicts[0].reason


def test_higher_confidence_wins(detector: ConflictDetector):
    """Test that higher confidence (>0.15 delta) wins over lower confidence when sources match."""
    now = datetime.now(timezone.utc)
    mem_low_conf = MemoryRecord(
        id="mem_low",
        user_id="user_1",
        content="Kubernetes cluster ingress controller is nginx ingress",
        source="agent",
        confidence=0.5,
        created_at=now,
        updated_at=now,
    )
    mem_high_conf = MemoryRecord(
        id="mem_high",
        user_id="user_1",
        content="Kubernetes cluster ingress controller is traefik ingress",
        source="agent",
        confidence=0.85,  # Delta = 0.35 (> 0.15)
        created_at=now - timedelta(minutes=10),
        updated_at=now - timedelta(minutes=10),
    )

    conflicts = detector.detect([mem_low_conf, mem_high_conf])
    assert len(conflicts) == 1
    assert conflicts[0].resolution_id == "mem_high_conf"
    assert "Confidence" in conflicts[0].reason


def test_multiple_conflicts(detector: ConflictDetector):
    """Test detecting and resolving multiple independent conflict pairs across candidate set."""
    now = datetime.now(timezone.utc)

    # Pair 1: Port conflict
    mem_port_1 = MemoryRecord(
        id="port_8080",
        user_id="user_multi",
        content="Application server listening port is 8080",
        confidence=0.8,
        updated_at=now - timedelta(days=1),
    )
    mem_port_2 = MemoryRecord(
        id="port_9090",
        user_id="user_multi",
        content="Application server listening port is 9090",
        confidence=0.8,
        updated_at=now,
    )

    # Pair 2: Database host conflict
    mem_db_1 = MemoryRecord(
        id="db_local",
        user_id="user_multi",
        content="Database host address is localhost 127.0.0.1",
        confidence=0.6,
        updated_at=now,
    )
    mem_db_2 = MemoryRecord(
        id="db_remote",
        user_id="user_multi",
        content="Database host address is db.internal.cluster.local",
        confidence=0.9,
        updated_at=now,
    )

    candidates = [mem_port_1, mem_port_2, mem_db_1, mem_db_2]
    conflicts = detector.detect(candidates)

    assert len(conflicts) == 2
    res_ids = {c.resolution_id for c in conflicts}
    assert "port_9090" in res_ids
    assert "db_remote" in res_ids
