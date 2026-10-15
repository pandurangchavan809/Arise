"""
Integration tests for FastAPI endpoints using TestClient.
Tests all routes: memory CRUD, quality recall, utility outcomes, archiving, forgetting, chat fallback, and stats.
"""

from typing import Generator
from fastapi.testclient import TestClient
import pytest

from adaptive_memory.config import Settings
from adaptive_memory.core.manager import MemoryQualityManager
from adaptive_memory.models import MemoryStatus, MemoryType, SafetyTier
from adaptive_memory.storage.sqlite import SQLiteStorage
from backend.app import app
from backend.dependencies import get_config, get_manager, get_storage


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """TestClient fixture with isolated in-memory SQLite storage."""
    test_settings = Settings(
        database_url="sqlite:///:memory:",
        log_level="DEBUG",
        max_memories=10,
        max_context_tokens=1500,
    )
    test_storage = SQLiteStorage(database_url="sqlite:///:memory:")

    # Initialize storage synchronously in test setup
    import asyncio
    asyncio.run(test_storage.initialize())
    test_manager = MemoryQualityManager(storage=test_storage, config=test_settings)

    async def override_storage():
        return test_storage

    async def override_manager():
        return test_manager

    def override_config():
        return test_settings

    app.dependency_overrides[get_storage] = override_storage
    app.dependency_overrides[get_manager] = override_manager
    app.dependency_overrides[get_config] = override_config

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    asyncio.run(test_storage.close())


def test_health_endpoint(client: TestClient):
    """Test health check endpoints return operational status."""
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"

    api_resp = client.get("/api/health")
    assert api_resp.status_code == 200
    data = api_resp.json()
    assert "status" in data
    assert data["storage_healthy"] is True


def test_create_memory(client: TestClient):
    """Test POST /api/memories creates a new memory record."""
    payload = {
        "content": "User prefers asynchronous Python programming with FastAPI",
        "user_id": "test_user_api",
        "memory_type": "long_term",
        "confidence": 0.9,
        "importance": 0.85,
        "risk_level": "T1",
        "source": "api_test",
    }
    resp = client.post("/api/memories", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert "memory" in data
    mem = data["memory"]
    assert mem["id"] is not None
    assert mem["content"] == payload["content"]
    assert mem["user_id"] == "test_user_api"
    assert mem["memory_type"] == "long_term"
    assert mem["confidence"] == 0.9


def test_get_memories(client: TestClient):
    """Test GET /api/memories lists records for user."""
    # Create two records
    client.post("/api/memories", json={"content": "Item A", "user_id": "u_list"})
    client.post("/api/memories", json={"content": "Item B", "user_id": "u_list"})

    resp = client.get("/api/memories", params={"user_id": "u_list"})
    assert resp.status_code == 200
    data = resp.json()
    assert "memories" in data
    assert data["total"] >= 2
    contents = [m["content"] for m in data["memories"]]
    assert "Item A" in contents
    assert "Item B" in contents


def test_get_memory_by_id(client: TestClient):
    """Test GET /api/memories/{memory_id} retrieves specific record."""
    created = client.post(
        "/api/memories",
        json={"content": "Lookup record by ID", "user_id": "u_get"},
    ).json()["memory"]
    mid = created["id"]

    resp = client.get(f"/api/memories/{mid}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["memory"]["id"] == mid
    assert data["memory"]["content"] == "Lookup record by ID"

    # Test non-existent ID returns 404
    missing_resp = client.get("/api/memories/nonexistent-id-999")
    assert missing_resp.status_code == 404


def test_delete_memory(client: TestClient):
    """Test DELETE /api/memories/{memory_id} removes memory."""
    created = client.post(
        "/api/memories",
        json={"content": "Record to delete", "user_id": "u_del"},
    ).json()["memory"]
    mid = created["id"]

    del_resp = client.delete(f"/api/memories/{mid}")
    assert del_resp.status_code == 200
    assert del_resp.json()["status"] == "success"

    # Confirm it is no longer found
    check_resp = client.get(f"/api/memories/{mid}")
    assert check_resp.status_code == 404


def test_recall_endpoint(client: TestClient):
    """Test POST /api/memory/recall returns scored memory candidates."""
    client.post(
        "/api/memories",
        json={
            "content": "Deployment target is Kubernetes with Helm charts",
            "user_id": "u_recall",
            "memory_type": "long_term",
            "confidence": 0.95,
        },
    )

    recall_payload = {
        "query": "Kubernetes Helm deployment",
        "user_id": "u_recall",
        "max_memories": 5,
        "max_tokens": 1000,
    }
    resp = client.post("/api/memory/recall", json=recall_payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "result" in data
    res = data["result"]
    assert res["query"] == recall_payload["query"]
    assert len(res["selected"]) >= 1
    first = res["selected"][0]
    assert "Kubernetes" in first["memory"]["content"]
    assert first["score"]["total"] > 0.0


def test_outcome_endpoint(client: TestClient):
    """Test POST /api/memory/outcome calibrates utility feedback."""
    created = client.post(
        "/api/memories",
        json={"content": "Helpful utility test", "user_id": "u_out"},
    ).json()["memory"]
    mid = created["id"]

    outcome_payload = {
        "memory_ids": [mid],
        "outcome": "helpful",
        "user_id": "u_out",
    }
    resp = client.post("/api/memory/outcome", json=outcome_payload)
    assert resp.status_code == 200
    assert resp.json()["status"] == "recorded"

    # Check that utility was updated from default 0.5 to ~0.65
    updated = client.get(f"/api/memories/{mid}").json()["memory"]
    assert updated["utility"] > 0.5


def test_forget_endpoint(client: TestClient):
    """Test POST /api/memory/forget removes memory."""
    created = client.post(
        "/api/memories",
        json={"content": "Sensitive secret to forget", "user_id": "u_forget"},
    ).json()["memory"]
    mid = created["id"]

    forget_payload = {"memory_id": mid, "user_id": "u_forget"}
    resp = client.post("/api/memory/forget", json=forget_payload)
    assert resp.status_code == 200
    assert resp.json()["status"] == "forgotten"

    # Verify memory is deleted
    assert client.get(f"/api/memories/{mid}").status_code == 404


def test_archive_endpoint(client: TestClient):
    """Test POST /api/memory/archive updates memory status to archived."""
    created = client.post(
        "/api/memories",
        json={"content": "Completed roadmap milestone", "user_id": "u_arc"},
    ).json()["memory"]
    mid = created["id"]

    archive_payload = {"memory_id": mid, "user_id": "u_arc"}
    resp = client.post("/api/memory/archive", json=archive_payload)
    assert resp.status_code == 200
    data = resp.json()["memory"]
    assert data["status"] == "archived"


def test_session_memories_endpoint(client: TestClient):
    """Test GET /api/memory/session lists only session memories."""
    client.post(
        "/api/memories",
        json={"content": "Session context item", "user_id": "u_sess", "memory_type": "session"},
    )
    client.post(
        "/api/memories",
        json={"content": "Long-term context item", "user_id": "u_sess", "memory_type": "long_term"},
    )

    resp = client.get("/api/memory/session", params={"user_id": "u_sess"})
    assert resp.status_code == 200
    memories = resp.json()["memories"]
    assert all(m["memory_type"] == "session" for m in memories)
    assert any("Session context item" in m["content"] for m in memories)


def test_long_term_memories_endpoint(client: TestClient):
    """Test GET /api/memory/long-term lists only long-term memories."""
    client.post(
        "/api/memories",
        json={"content": "Core identity trait", "user_id": "u_lt", "memory_type": "long_term"},
    )

    resp = client.get("/api/memory/long-term", params={"user_id": "u_lt"})
    assert resp.status_code == 200
    memories = resp.json()["memories"]
    assert all(m["memory_type"] == "long_term" for m in memories)
    assert any("Core identity trait" in m["content"] for m in memories)


def test_experience_memories_endpoint(client: TestClient):
    """Test GET /api/memory/experience lists procedural experience memories."""
    client.post(
        "/api/memories",
        json={"content": "Optimization trial result", "user_id": "u_exp", "memory_type": "experience"},
    )

    resp = client.get("/api/memory/experience", params={"user_id": "u_exp"})
    assert resp.status_code == 200
    memories = resp.json()["memories"]
    assert all(m["memory_type"] == "experience" for m in memories)
    assert any("Optimization trial result" in m["content"] for m in memories)


def test_prospective_memories_endpoint(client: TestClient):
    """Test GET /api/memory/prospective lists task/reminder memories."""
    client.post(
        "/api/memories",
        json={"content": "Scheduled maintenance tomorrow", "user_id": "u_pro", "memory_type": "prospective"},
    )

    resp = client.get("/api/memory/prospective", params={"user_id": "u_pro"})
    assert resp.status_code == 200
    memories = resp.json()["memories"]
    assert all(m["memory_type"] == "prospective" for m in memories)
    assert any("Scheduled maintenance tomorrow" in m["content"] for m in memories)


def test_chat_without_llm(client: TestClient):
    """Test POST /api/chat gracefully handles unconfigured LLM credentials without raising 500."""
    # Pre-populate memory to verify recall in chat context
    client.post(
        "/api/memories",
        json={"content": "User prefers dark mode editor theme", "user_id": "u_chat"},
    )

    chat_payload = {
        "message": "What is my preferred editor theme?",
        "user_id": "u_chat",
        "use_memory": True,
        "use_search": False,
    }
    resp = client.post("/api/chat", json=chat_payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "response" in data
    # Should contain graceful fallback message mentioning Nebius API key or memory retrieval
    assert len(data["response"]) > 0
    assert "memories_used" in data


def test_stats_endpoint(client: TestClient):
    """Test GET /api/stats returns comprehensive aggregate metrics."""
    client.post(
        "/api/memories",
        json={"content": "Metric sample 1", "user_id": "u_stats", "memory_type": "long_term"},
    )
    client.post(
        "/api/memories",
        json={"content": "Metric sample 2", "user_id": "u_stats", "memory_type": "session"},
    )

    resp = client.get("/api/stats", params={"user_id": "u_stats"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["user_id"] == "u_stats"
    stats = data["stats"]
    assert stats["total_memories"] >= 2
    assert "counts_by_type" in stats
    assert "average_utility" in stats
    assert "average_confidence" in stats
