"""
Pydantic API request and response schemas for FastAPI endpoints.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from adaptive_memory.models import (
    EdgeBudget,
    MemoryCandidate,
    MemoryRecord,
    MemoryStatus,
    MemoryType,
    OutcomeType,
    RecallResult,
    SafetyTier,
)


class CreateMemoryRequest(BaseModel):
    """Payload to create a new memory."""
    content: str = Field(..., description="Memory content text")
    user_id: str = Field(..., description="Owning user identifier")
    memory_type: MemoryType = Field(default=MemoryType.SESSION, description="Memory category")
    source: str = Field(default="user", description="Origin of memory")
    task_context: Optional[str] = Field(default=None, description="Task context description")
    confidence: float = Field(default=0.5, ge=0.0, le=1.0, description="Confidence score")
    importance: float = Field(default=0.5, ge=0.0, le=1.0, description="Inherent importance score")
    risk_level: SafetyTier = Field(default=SafetyTier.T0_CASUAL, description="Safety tier")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    expires_at: Optional[datetime] = Field(default=None, description="Optional ISO timestamp expiration")


class UpdateMemoryRequest(BaseModel):
    """Payload to update an existing memory."""
    content: Optional[str] = None
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    utility: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    importance: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    risk_level: Optional[SafetyTier] = None
    status: Optional[MemoryStatus] = None
    task_context: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class MemoryResponse(BaseModel):
    """Response containing full memory record."""
    memory: MemoryRecord


class ListMemoriesResponse(BaseModel):
    """Paginated list of memories."""
    memories: List[MemoryRecord]
    total: int
    user_id: Optional[str] = None


class RecallRequest(BaseModel):
    """Payload for memory recall query."""
    query: str = Field(..., description="Query for memory retrieval")
    user_id: str = Field(..., description="User identifier")
    max_memories: Optional[int] = Field(default=None, description="Override max memory count")
    max_tokens: Optional[int] = Field(default=None, description="Override token budget")
    memory_types: Optional[List[MemoryType]] = Field(default=None, description="Specific memory types to recall")
    situation: Optional[str] = Field(default=None, description="Optional current task context or situation")


class RecallResponse(BaseModel):
    """Recall pipeline result response."""
    result: RecallResult


class OutcomeRequest(BaseModel):
    """Outcome feedback payload to calibrate memory utility."""
    memory_ids: List[str] = Field(..., description="Target memory IDs evaluated")
    outcome: OutcomeType = Field(..., description="Outcome feedback value")
    user_id: str = Field(..., description="User ID associated with the memories")


class ForgetRequest(BaseModel):
    """Payload to delete memory."""
    memory_id: str
    user_id: str


class ArchiveRequest(BaseModel):
    """Payload to archive memory."""
    memory_id: str
    user_id: str


class PromoteRequest(BaseModel):
    """Payload to promote memory type."""
    memory_id: str
    target_type: MemoryType = MemoryType.LONG_TERM


class ChatRequest(BaseModel):
    """Augmented chat completion request."""
    message: str = Field(..., description="User input message")
    user_id: str = Field(default="default_user", description="User identifier")
    session_id: Optional[str] = Field(default=None, description="Session identifier")
    use_memory: bool = Field(default=True, description="Whether to inject relevant memories")
    use_search: bool = Field(default=False, description="Whether to query live web search")


class ChatResponse(BaseModel):
    """Augmented chat completion response."""
    response: str
    memories_used: List[MemoryCandidate] = Field(default_factory=list)
    search_results: List[Dict[str, Any]] = Field(default_factory=list)
    memories_extracted: List[MemoryRecord] = Field(default_factory=list)


class SearchRequest(BaseModel):
    """External web search request."""
    query: str = Field(..., description="Search query string")
    max_results: int = Field(default=5, ge=1, le=20, description="Max results")


class TranscribeRequest(BaseModel):
    """Base64 audio transcription request."""
    audio_base64: str = Field(..., description="Base64-encoded audio payload")
    mime_type: str = Field(default="audio/wav", description="Audio MIME type")


class SpeakRequest(BaseModel):
    """Text-to-speech synthesis request."""
    text: str = Field(..., description="Text to synthesize")
    voice: Optional[str] = Field(default=None, description="Voice identifier")


class HealthResponse(BaseModel):
    """System health status response."""
    status: str
    storage_healthy: bool
    llm_available: bool
    search_available: bool
    speech_available: bool
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class StatsResponse(BaseModel):
    """System and user memory statistics."""
    user_id: str
    stats: Dict[str, Any]
