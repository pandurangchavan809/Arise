"""
Unit tests for the Adaptive Memory Python SDK Client.
Verifies client instantiation, request construction, response parsing, and error mapping.
"""

from unittest.mock import MagicMock, patch
import httpx
import pytest

from adaptive_memory_sdk import Memory
from adaptive_memory_sdk.exceptions import (
    AdaptiveMemoryError,
    ConnectionError,
    NotFoundError,
    ValidationError,
)
from adaptive_memory_sdk.models import RecallResult


@pytest.fixture
def memory_client() -> Memory:
    return Memory(base_url="http://testserver:8000")


def test_client_init():
    """Test SDK client initialization with custom parameters."""
    client = Memory(base_url="http://custom:9000/", api_key="secret-token", timeout=15.0)
    assert client.base_url == "http://custom:9000"
    assert client.api_key == "secret-token"
    assert client.timeout == 15.0
    client.close()


def test_client_context_manager():
    """Test Memory client functions as context manager."""
    with Memory(base_url="http://test:8000") as mem:
        assert mem.base_url == "http://test:8000"


def test_remember(memory_client: Memory):
    """Test remember call serializes parameters and returns response dict."""
    mock_resp = MagicMock()
    mock_resp.status_code = 201
    mock_resp.json.return_value = {
        "memory": {
            "id": "mem_123",
            "content": "Test SDK remember",
            "user_id": "u1",
            "memory_type": "long_term",
        }
    }

    with patch.object(memory_client, "_request", return_value=mock_resp) as mock_req:
        res = memory_client.remember(
            content="Test SDK remember",
            user_id="u1",
            memory_type="long_term",
            confidence=0.9,
        )

        assert res["id"] == "mem_123"
        mock_req.assert_called_once()
        args, kwargs = mock_req.call_args
        assert args[0] == "POST"
        assert args[1] == "/api/memories"
        assert kwargs["json"]["content"] == "Test SDK remember"


def test_recall(memory_client: Memory):
    """Test recall call parses result into RecallResult Pydantic model."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "result": {
            "query": "Kubernetes cluster",
            "candidates": [],
            "selected": [
                {
                    "memory": {
                        "id": "m1",
                        "user_id": "u1",
                        "content": "Kubernetes cluster on AWS",
                        "memory_type": "long_term",
                    },
                    "score": {"total": 0.88, "relevance": 0.9},
                    "decision": {"decision": "included", "reason": "High relevance"},
                }
            ],
            "suppressed": [],
            "budget_applied": {"max_memories": 10, "max_context_tokens": 2000},
            "total_candidates": 1,
        }
    }

    with patch.object(memory_client, "_request", return_value=mock_resp):
        recall_res = memory_client.recall(query="Kubernetes cluster", user_id="u1")

        assert isinstance(recall_res, RecallResult)
        assert recall_res.query == "Kubernetes cluster"
        assert len(recall_res.selected) == 1
        assert recall_res.selected[0].memory.content == "Kubernetes cluster on AWS"
        assert len(recall_res.memories) == 1


def test_record_outcome(memory_client: Memory):
    """Test record_outcome formats memory_ids and outcome string."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"status": "recorded"}

    with patch.object(memory_client, "_request", return_value=mock_resp) as mock_req:
        memory_client.record_outcome(memory_ids="mem_1", outcome="helpful", user_id="u1")

        args, kwargs = mock_req.call_args
        assert args[0] == "POST"
        assert kwargs["json"]["memory_ids"] == ["mem_1"]
        assert kwargs["json"]["outcome"] == "helpful"


def test_forget(memory_client: Memory):
    """Test forget issues forget request."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"status": "forgotten"}

    with patch.object(memory_client, "_request", return_value=mock_resp) as mock_req:
        memory_client.forget(memory_id="mem_1", user_id="u1")
        mock_req.assert_called_once()


def test_archive(memory_client: Memory):
    """Test archive issues archive request."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"status": "archived"}

    with patch.object(memory_client, "_request", return_value=mock_resp) as mock_req:
        memory_client.archive(memory_id="mem_1", user_id="u1")
        mock_req.assert_called_once()


def test_error_mapping_404(memory_client: Memory):
    """Test that HTTP 404 raises NotFoundError."""
    mock_resp = httpx.Response(status_code=404, json={"detail": "Memory not found"})
    with patch.object(memory_client._client, "request", return_value=mock_resp):
        with pytest.raises(NotFoundError) as exc_info:
            memory_client.get_memory("invalid_id")
        assert "Memory not found" in str(exc_info.value)
        assert exc_info.value.status_code == 404


def test_error_mapping_422(memory_client: Memory):
    """Test that HTTP 422 raises ValidationError."""
    mock_resp = httpx.Response(status_code=422, json={"detail": "Missing content"})
    with patch.object(memory_client._client, "request", return_value=mock_resp):
        with pytest.raises(ValidationError) as exc_info:
            memory_client.remember(content="", user_id="u1")
        assert exc_info.value.status_code == 422


def test_error_mapping_connection(memory_client: Memory):
    """Test that network connection failures raise ConnectionError."""
    with patch.object(
        memory_client._client,
        "request",
        side_effect=httpx.ConnectError("Connection refused"),
    ):
        with pytest.raises(ConnectionError) as exc_info:
            memory_client.health()
        assert "Failed to connect" in str(exc_info.value)
