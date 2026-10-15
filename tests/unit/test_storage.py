"""
Unit tests for SQLiteStorage: CRUD operations, FTS5 full-text indexing, filtering, and schema integrity.
"""

from datetime import datetime, timedelta, timezone
import pytest

from adaptive_memory.models import MemoryRecord, MemoryStatus, MemoryType, SafetyTier
from adaptive_memory.storage.sqlite import SQLiteStorage


@pytest.mark.asyncio
async def test_store_and_retrieve(storage: SQLiteStorage):
    """Test storing and subsequently retrieving a MemoryRecord by ID."""
    rec = MemoryRecord(
        user_id="user_store",
        content="Microservices communicate via gRPC on internal network",
        memory_type=MemoryType.LONG_TERM,
        confidence=0.88,
        importance=0.75,
        risk_level=SafetyTier.T2_OPERATIONAL,
        metadata={"service": "gateway"},
    )
    await storage.store(rec)

    retrieved = await storage.get(rec.id)
    assert retrieved is not None
    assert retrieved.id == rec.id
    assert retrieved.content == rec.content
    assert retrieved.memory_type == MemoryType.LONG_TERM
    assert retrieved.confidence == 0.88
    assert retrieved.risk_level == SafetyTier.T2_OPERATIONAL
    assert retrieved.metadata.get("service") == "gateway"


@pytest.mark.asyncio
async def test_search_fts(storage: SQLiteStorage):
    """Test FTS5 full-text retrieval matching query terms against content."""
    rec1 = MemoryRecord(
        user_id="user_fts",
        content="Deploying FastAPI applications with Docker containers",
        memory_type=MemoryType.EXPERIENCE,
    )
    rec2 = MemoryRecord(
        user_id="user_fts",
        content="Configuring MySQL relational database clusters",
        memory_type=MemoryType.EXPERIENCE,
    )
    await storage.store(rec1)
    await storage.store(rec2)

    results = await storage.search(query="FastAPI Docker", user_id="user_fts")
    assert len(results) >= 1
    found_ids = [r.id for r in results]
    assert rec1.id in found_ids
    assert rec2.id not in found_ids


@pytest.mark.asyncio
async def test_update_memory(storage: SQLiteStorage):
    """Test updating fields of an existing memory record."""
    rec = MemoryRecord(
        user_id="user_upd",
        content="Original initial description",
        memory_type=MemoryType.SESSION,
        confidence=0.5,
    )
    await storage.store(rec)

    updated = await storage.update(
        rec.id,
        {
            "content": "Updated enhanced description",
            "confidence": 0.95,
        },
    )

    assert updated.content == "Updated enhanced description"
    assert updated.confidence == 0.95

    # Verify persisted state
    fetched = await storage.get(rec.id)
    assert fetched.content == "Updated enhanced description"
    assert fetched.confidence == 0.95


@pytest.mark.asyncio
async def test_delete_memory(storage: SQLiteStorage):
    """Test permanently deleting a memory record."""
    rec = MemoryRecord(
        user_id="user_del",
        content="Delete target item",
        memory_type=MemoryType.SESSION,
    )
    await storage.store(rec)

    deleted = await storage.delete(rec.id)
    assert deleted is True

    # Confirm it is no longer retrievable
    retrieved = await storage.get(rec.id)
    assert retrieved is None


@pytest.mark.asyncio
async def test_list_by_type(storage: SQLiteStorage):
    """Test filtering memories by user and memory_type."""
    mem_session = MemoryRecord(
        user_id="user_type",
        content="Short lived session memory",
        memory_type=MemoryType.SESSION,
    )
    mem_long = MemoryRecord(
        user_id="user_type",
        content="Permanent long term preference",
        memory_type=MemoryType.LONG_TERM,
    )
    await storage.store(mem_session)
    await storage.store(mem_long)

    session_list = await storage.list_by_type(user_id="user_type", memory_type=MemoryType.SESSION)
    assert any(m.id == mem_session.id for m in session_list)
    assert not any(m.id == mem_long.id for m in session_list)

    long_list = await storage.list_by_type(user_id="user_type", memory_type=MemoryType.LONG_TERM)
    assert any(m.id == mem_long.id for m in long_list)
    assert not any(m.id == mem_session.id for m in long_list)


@pytest.mark.asyncio
async def test_get_expired(storage: SQLiteStorage):
    """Test querying records whose expires_at timestamp is prior to reference cutoff."""
    now = datetime.now(timezone.utc)
    expired_rec = MemoryRecord(
        user_id="user_exp",
        content="Expired authentication session",
        memory_type=MemoryType.SESSION,
        status=MemoryStatus.ACTIVE,
        expires_at=now - timedelta(hours=1),
    )
    active_rec = MemoryRecord(
        user_id="user_exp",
        content="Valid active authentication session",
        memory_type=MemoryType.SESSION,
        status=MemoryStatus.ACTIVE,
        expires_at=now + timedelta(hours=5),
    )
    await storage.store(expired_rec)
    await storage.store(active_rec)

    expired_list = await storage.get_expired(before=now)
    assert any(m.id == expired_rec.id for m in expired_list)
    assert not any(m.id == active_rec.id for m in expired_list)


@pytest.mark.asyncio
async def test_indexes_created(storage: SQLiteStorage):
    """Test that all required SQLite indexes and FTS virtual table exist."""
    db = await storage._get_connection()
    async with db.execute("SELECT name FROM sqlite_master WHERE type='index'") as cursor:
        rows = await cursor.fetchall()
        index_names = {row["name"] for row in rows}

    assert "idx_memories_user_id" in index_names
    assert "idx_memories_type" in index_names
    assert "idx_memories_status" in index_names
    assert "idx_memories_created_at" in index_names
    assert "idx_memories_confidence" in index_names
    assert "idx_memories_utility" in index_names

    # Verify FTS table exists
    async with db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='memories_fts'") as cursor:
        fts_table = await cursor.fetchone()
        assert fts_table is not None
