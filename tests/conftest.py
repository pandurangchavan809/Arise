"""
Pytest configuration and shared fixtures for Adaptive Memory Runtime tests.
"""

import asyncio
from datetime import datetime, timedelta, timezone
from typing import AsyncGenerator, List
import pytest
import pytest_asyncio

from adaptive_memory.config import Settings
from adaptive_memory.core.manager import MemoryQualityManager
from adaptive_memory.models import (
    EdgeBudget,
    MemoryRecord,
    MemoryStatus,
    MemoryType,
    SafetyTier,
)
from adaptive_memory.storage.sqlite import SQLiteStorage


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def config() -> Settings:
    """Fixture providing testing settings with low budget defaults."""
    return Settings(
        database_url="sqlite:///:memory:",
        log_level="DEBUG",
        max_memories=5,
        max_context_tokens=1000,
        max_latency_ms=50,
        max_storage_bytes=10485760,
    )


@pytest_asyncio.fixture
async def storage() -> AsyncGenerator[SQLiteStorage, None]:
    """Fixture providing an initialized in-memory SQLiteStorage."""
    store = SQLiteStorage(database_url="sqlite:///:memory:")
    await store.initialize()
    yield store
    await store.close()


@pytest_asyncio.fixture
async def manager(storage: SQLiteStorage, config: Settings) -> MemoryQualityManager:
    """Fixture providing a configured MemoryQualityManager instance."""
    return MemoryQualityManager(storage=storage, config=config)


@pytest_asyncio.fixture
async def sample_memories(storage: SQLiteStorage) -> List[MemoryRecord]:
    """Fixture providing a pre-populated set of diverse test memories."""
    now = datetime.now(timezone.utc)
    records = [
        MemoryRecord(
            user_id="user_test",
            content="User prefers Python and FastAPI for microservices architecture",
            memory_type=MemoryType.LONG_TERM,
            confidence=0.9,
            importance=0.8,
            utility=0.7,
            risk_level=SafetyTier.T1_PERSONAL,
            source="user",
            task_context="architecture_decision",
            status=MemoryStatus.ACTIVE,
            created_at=now - timedelta(days=2),
            updated_at=now - timedelta(days=1),
        ),
        MemoryRecord(
            user_id="user_test",
            content="Docker multi-stage builds reduced final container footprint by 65 percent",
            memory_type=MemoryType.EXPERIENCE,
            confidence=0.85,
            importance=0.75,
            utility=0.8,
            risk_level=SafetyTier.T2_OPERATIONAL,
            source="agent",
            task_context="docker_build",
            status=MemoryStatus.ACTIVE,
            created_at=now - timedelta(hours=5),
            updated_at=now - timedelta(hours=3),
        ),
        MemoryRecord(
            user_id="user_test",
            content="Active debugging session on port 8000 connection timeout",
            memory_type=MemoryType.SESSION,
            confidence=0.95,
            importance=0.4,
            utility=0.5,
            risk_level=SafetyTier.T0_CASUAL,
            source="user",
            task_context="session_alpha_123",
            status=MemoryStatus.ACTIVE,
            expires_at=now + timedelta(hours=1),
            created_at=now - timedelta(minutes=30),
            updated_at=now - timedelta(minutes=10),
            metadata={"session_id": "session_alpha_123"},
        ),
        MemoryRecord(
            user_id="user_test",
            content="Schedule quarterly security dependency audit on Monday 9 AM",
            memory_type=MemoryType.PROSPECTIVE,
            confidence=0.9,
            importance=0.9,
            utility=0.6,
            risk_level=SafetyTier.T3_SENSITIVE,
            source="user",
            task_context="compliance_review",
            status=MemoryStatus.ACTIVE,
            created_at=now - timedelta(hours=1),
            updated_at=now - timedelta(hours=1),
        ),
    ]

    stored_records = []
    for r in records:
        stored = await storage.store(r)
        stored_records.append(stored)

    return stored_records
