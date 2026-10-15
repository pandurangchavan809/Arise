"""
Adaptive Memory Python SDK Client.
Provides a synchronous client for interacting with the Adaptive Memory Runtime REST API.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union
import httpx

from adaptive_memory_sdk.exceptions import (
    AdaptiveMemoryError,
    ConnectionError,
    NotFoundError,
    ValidationError,
)
from adaptive_memory_sdk.models import (
    MemoryCandidate,
    MemoryRecord,
    QualityDecision,
    QualityScore,
    RecallResult,
)


class Memory:
    """Client for the Adaptive Memory Runtime REST API."""

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        api_key: Optional[str] = None,
        timeout: float = 30.0,
    ) -> None:
        """Initialize the Adaptive Memory client.

        Args:
            base_url: The base URL of the Adaptive Memory server.
            api_key: Optional API key for authentication.
            timeout: Request timeout in seconds.
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "AdaptiveMemorySDK/0.1.0",
        }
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        self._client = httpx.Client(
            base_url=self.base_url,
            headers=headers,
            timeout=timeout,
        )

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._client.close()

    def __enter__(self) -> "Memory":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        fallback_paths: Optional[List[str]] = None,
    ) -> httpx.Response:
        """Execute HTTP request with robust error handling and fallback route resolution."""
        all_paths = [path] + (fallback_paths or [])
        last_resp = None

        for idx, candidate_path in enumerate(all_paths):
            try:
                resp = self._client.request(
                    method=method,
                    url=candidate_path,
                    params={k: v for k, v in (params or {}).items() if v is not None},
                    json=json,
                )
                last_resp = resp
                if resp.status_code == 404 and idx < len(all_paths) - 1:
                    continue
                break
            except httpx.ConnectError as e:
                raise ConnectionError(
                    f"Failed to connect to Adaptive Memory service at {self.base_url}: {e}"
                ) from e
            except httpx.TimeoutException as e:
                raise ConnectionError(
                    f"Request to {candidate_path} timed out after {self.timeout}s: {e}"
                ) from e
            except httpx.RequestError as e:
                raise ConnectionError(f"HTTP request error: {e}") from e

        if last_resp is None:
            raise ConnectionError(f"No response received from {path}")

        return self._handle_response(last_resp)

    def _handle_response(self, response: httpx.Response) -> httpx.Response:
        """Inspect HTTP response and raise appropriate typed exceptions on failure."""
        if 200 <= response.status_code < 300:
            return response

        try:
            error_data = response.json()
            message = error_data.get("detail", error_data.get("message", response.text))
        except Exception:
            error_data = {}
            message = response.text or f"HTTP {response.status_code}"

        if response.status_code == 404:
            raise NotFoundError(message=message, status_code=404, details=error_data)
        elif response.status_code == 422:
            raise ValidationError(message=message, status_code=422, details=error_data)
        elif response.status_code in (400, 409):
            raise ValidationError(message=message, status_code=response.status_code, details=error_data)
        else:
            raise AdaptiveMemoryError(
                message=message,
                status_code=response.status_code,
                details=error_data,
            )

    # -------------------------------------------------------------------------
    # Core Memory Operations
    # -------------------------------------------------------------------------

    def remember(
        self,
        content: str,
        memory_type: str = "long_term",
        user_id: str = "default",
        source: str = "sdk",
        confidence: float = 0.5,
        importance: float = 0.5,
        risk_level: str = "T0_CASUAL",
        metadata: Optional[Dict[str, Any]] = None,
        expires_at: Optional[str] = None,
        task_context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Store a new memory.

        Args:
            content: The text content of the memory.
            memory_type: session, long_term, experience, or prospective.
            user_id: User or agent identifier.
            source: Origin of memory (default: 'sdk').
            confidence: Confidence score [0, 1].
            importance: Inherent importance [0, 1].
            risk_level: Risk tier (e.g. T0_CASUAL, T1_PERSONAL).
            metadata: Optional dictionary of custom attributes.
            expires_at: Optional ISO8601 expiry timestamp string.
            task_context: Optional task/domain context string.

        Returns:
            Dict containing the created memory record.
        """
        payload = {
            "content": content,
            "memory_type": memory_type,
            "user_id": user_id,
            "source": source,
            "confidence": confidence,
            "importance": importance,
            "risk_level": risk_level,
            "metadata": metadata or {},
            "expires_at": expires_at,
            "task_context": task_context,
        }
        resp = self._request(
            "POST",
            "/api/memories",
            json=payload,
            fallback_paths=["/memories"],
        )
        data = resp.json()
        if isinstance(data, dict) and "memory" in data:
            return data["memory"]
        return data

    def recall(
        self,
        query: str,
        user_id: str = "default",
        max_memories: int = 10,
        max_tokens: int = 2000,
        memory_types: Optional[List[str]] = None,
    ) -> RecallResult:
        """Recall relevant memories matching a query.

        Args:
            query: The recall query string.
            user_id: User or agent identifier.
            max_memories: Max number of memories to return.
            max_tokens: Maximum token budget for returned memories.
            memory_types: Optional list of memory types to filter by.

        Returns:
            RecallResult containing selected memories, candidates, and budget details.
        """
        payload = {
            "query": query,
            "user_id": user_id,
            "max_memories": max_memories,
            "max_tokens": max_tokens,
            "memory_types": memory_types,
        }
        resp = self._request(
            "POST",
            "/api/memory/recall",
            json=payload,
            fallback_paths=["/api/recall", "/recall"],
        )
        data = resp.json()
        result_data = data.get("result", data) if isinstance(data, dict) else data
        return RecallResult.model_validate(result_data)

    def record_outcome(
        self,
        memory_ids: Union[str, List[str]],
        outcome: str,
        user_id: str = "default",
    ) -> None:
        """Record utility feedback for recalled memories.

        Args:
            memory_ids: A single memory ID or list of memory IDs.
            outcome: 'helpful', 'irrelevant', or 'misleading'.
            user_id: User or agent identifier.
        """
        if isinstance(memory_ids, str):
            memory_ids = [memory_ids]

        payload = {
            "memory_ids": memory_ids,
            "outcome": outcome,
            "user_id": user_id,
        }
        self._request(
            "POST",
            "/api/memory/outcome",
            json=payload,
            fallback_paths=["/api/outcomes", "/api/memories/outcome", "/outcomes"],
        )

    def forget(self, memory_id: str, user_id: str = "default") -> None:
        """Explicitly forget / suppress a memory.

        Args:
            memory_id: The ID of the memory to forget.
            user_id: User or agent identifier.
        """
        payload = {"memory_id": memory_id, "user_id": user_id}
        self._request(
            "POST",
            "/api/memory/forget",
            json=payload,
            fallback_paths=[
                f"/api/memories/{memory_id}/forget",
                f"/memories/{memory_id}/forget",
            ],
        )

    def archive(self, memory_id: str, user_id: str = "default") -> None:
        """Archive an active memory.

        Args:
            memory_id: The ID of the memory to archive.
            user_id: User or agent identifier.
        """
        payload = {"memory_id": memory_id, "user_id": user_id}
        self._request(
            "POST",
            "/api/memory/archive",
            json=payload,
            fallback_paths=[
                f"/api/memories/{memory_id}/archive",
                f"/memories/{memory_id}/archive",
            ],
        )

    def get_memories(
        self,
        user_id: str = "default",
        memory_type: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List memories with optional type and status filtering.

        Args:
            user_id: User identifier.
            memory_type: Optional memory type filter.
            status: Optional status filter (active, archived, expired, suppressed).

        Returns:
            List of memory records as dictionaries.
        """
        params = {"user_id": user_id}
        if memory_type:
            params["memory_type"] = memory_type
        if status:
            params["status"] = status

        resp = self._request(
            "GET",
            "/api/memories",
            params=params,
            fallback_paths=["/memories"],
        )
        data = resp.json()
        if isinstance(data, dict) and "memories" in data:
            return data["memories"]
        return data if isinstance(data, list) else []

    def get_memory(self, memory_id: str) -> Dict[str, Any]:
        """Retrieve a specific memory by its ID.

        Args:
            memory_id: Unique memory ID.

        Returns:
            Dict containing the memory record.
        """
        resp = self._request(
            "GET",
            f"/api/memories/{memory_id}",
            fallback_paths=[f"/memories/{memory_id}"],
        )
        data = resp.json()
        if isinstance(data, dict) and "memory" in data:
            return data["memory"]
        return data

    def delete_memory(self, memory_id: str) -> None:
        """Permanently delete a memory by its ID.

        Args:
            memory_id: Unique memory ID.
        """
        self._request(
            "DELETE",
            f"/api/memories/{memory_id}",
            fallback_paths=[f"/memories/{memory_id}"],
        )

    # -------------------------------------------------------------------------
    # Specialized Memory Type Fetchers
    # -------------------------------------------------------------------------

    def get_session_memories(self, user_id: str = "default") -> List[Dict[str, Any]]:
        """Retrieve all active session memories for a user."""
        try:
            resp = self._request(
                "GET",
                "/api/memory/session",
                params={"user_id": user_id},
                fallback_paths=["/api/memories/session"],
            )
            data = resp.json()
            return data.get("memories", data) if isinstance(data, dict) else data
        except (NotFoundError, AdaptiveMemoryError):
            return self.get_memories(user_id=user_id, memory_type="session")

    def get_long_term_memories(self, user_id: str = "default") -> List[Dict[str, Any]]:
        """Retrieve all active long-term memories for a user."""
        try:
            resp = self._request(
                "GET",
                "/api/memory/long-term",
                params={"user_id": user_id},
                fallback_paths=["/api/memories/long-term"],
            )
            data = resp.json()
            return data.get("memories", data) if isinstance(data, dict) else data
        except (NotFoundError, AdaptiveMemoryError):
            return self.get_memories(user_id=user_id, memory_type="long_term")

    def get_experience_memories(self, user_id: str = "default") -> List[Dict[str, Any]]:
        """Retrieve all active experience memories for a user."""
        try:
            resp = self._request(
                "GET",
                "/api/memory/experience",
                params={"user_id": user_id},
                fallback_paths=["/api/memories/experience"],
            )
            data = resp.json()
            return data.get("memories", data) if isinstance(data, dict) else data
        except (NotFoundError, AdaptiveMemoryError):
            return self.get_memories(user_id=user_id, memory_type="experience")

    def get_prospective_memories(self, user_id: str = "default") -> List[Dict[str, Any]]:
        """Retrieve all active prospective/task-based memories for a user."""
        try:
            resp = self._request(
                "GET",
                "/api/memory/prospective",
                params={"user_id": user_id},
                fallback_paths=["/api/memories/prospective"],
            )
            data = resp.json()
            return data.get("memories", data) if isinstance(data, dict) else data
        except (NotFoundError, AdaptiveMemoryError):
            return self.get_memories(user_id=user_id, memory_type="prospective")

    # -------------------------------------------------------------------------
    # Chat & Search
    # -------------------------------------------------------------------------

    def chat(
        self,
        message: str,
        user_id: str = "default",
        session_id: Optional[str] = None,
        use_memory: bool = True,
        use_search: bool = False,
    ) -> Dict[str, Any]:
        """Send a chat message with memory grounding and optional web search.

        Args:
            message: User prompt or message.
            user_id: User identifier.
            session_id: Conversation session identifier.
            use_memory: Whether to inject retrieved memories into context.
            use_search: Whether to enable Tavily web search.

        Returns:
            Dict containing assistant response and metadata.
        """
        payload = {
            "message": message,
            "user_id": user_id,
            "session_id": session_id,
            "use_memory": use_memory,
            "use_search": use_search,
        }
        resp = self._request(
            "POST",
            "/api/chat",
            json=payload,
            fallback_paths=["/chat"],
        )
        return resp.json()

    def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Perform a web search using Tavily.

        Args:
            query: Search query text.
            max_results: Max results to return.

        Returns:
            List of search result dictionaries.
        """
        try:
            resp = self._request(
                "POST",
                "/api/search",
                json={"query": query, "max_results": max_results},
                fallback_paths=["/search"],
            )
        except (NotFoundError, ValidationError, AdaptiveMemoryError):
            resp = self._request(
                "GET",
                "/api/search",
                params={"query": query, "max_results": max_results},
                fallback_paths=["/search"],
            )
        data = resp.json()
        if isinstance(data, dict) and "results" in data:
            return data["results"]
        return data if isinstance(data, list) else []

    # -------------------------------------------------------------------------
    # Diagnostics & System Information
    # -------------------------------------------------------------------------

    def health(self) -> Dict[str, Any]:
        """Check server health status."""
        resp = self._request(
            "GET",
            "/health",
            fallback_paths=["/api/health"],
        )
        return resp.json()

    def stats(self, user_id: str = "default") -> Dict[str, Any]:
        """Retrieve runtime memory statistics."""
        resp = self._request(
            "GET",
            "/api/stats",
            params={"user_id": user_id},
            fallback_paths=["/stats"],
        )
        data = resp.json()
        if isinstance(data, dict) and "stats" in data:
            return data["stats"]
        return data
