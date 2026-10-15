"""
Data models and response types for the Adaptive Memory Python SDK.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
import uuid

from pydantic import BaseModel, Field


class MemoryRecord(BaseModel):
    """Represents a discrete memory unit in the Adaptive Memory Runtime."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = Field(default="default", description="Owner ID")
    content: str = Field(..., description="Memory content text")
    memory_type: str = Field(default="long_term", description="Memory classification (session, long_term, experience, prospective)")
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    importance: float = Field(default=0.5, ge=0.0, le=1.0)
    utility: float = Field(default=0.5, ge=0.0, le=1.0)
    recency: float = Field(default=1.0, ge=0.0, le=1.0)
    risk_level: str = Field(default="T0_CASUAL")
    source: str = Field(default="sdk")
    status: str = Field(default="active")
    access_count: int = Field(default=0)
    task_context: Optional[str] = Field(default=None)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[Any] = Field(default=None)
    updated_at: Optional[Any] = Field(default=None)
    expires_at: Optional[Any] = Field(default=None)
    embedding: Optional[List[float]] = Field(default=None)


class QualityScore(BaseModel):
    """Breakdown of quality scores across dimensions."""
    relevance: float = Field(default=0.0)
    utility: float = Field(default=0.0)
    confidence: float = Field(default=0.0)
    recency: float = Field(default=0.0)
    conflict_risk: float = Field(default=0.0)
    total: float = Field(default=0.0)
    explanation: Optional[Dict[str, Any]] = Field(default=None)

    @property
    def total_score(self) -> float:
        """Alias for total score."""
        return self.total


class QualityDecision(BaseModel):
    """Decision made by the Quality Manager for memory candidates."""
    decision: str = Field(default="included", description="Decision outcome ('included' or 'suppressed')")
    reason: Optional[str] = Field(default=None, description="Explanation for decision")
    details: Optional[Dict[str, Any]] = Field(default=None)


class MemoryCandidate(BaseModel):
    """A candidate memory paired with its evaluated quality score and inclusion decision."""
    memory: MemoryRecord
    score: Optional[QualityScore] = None
    decision: Optional[QualityDecision] = None
    relevance: float = Field(default=0.0)


class RecallResult(BaseModel):
    """Comprehensive result of a memory recall query."""
    query: str
    memories: List[MemoryRecord] = Field(default_factory=list)
    candidates: List[MemoryCandidate] = Field(default_factory=list)
    selected: List[MemoryCandidate] = Field(default_factory=list)
    suppressed: List[MemoryCandidate] = Field(default_factory=list)
    total_found: int = Field(default=0)
    total_candidates: int = Field(default=0)
    total_tokens: int = Field(default=0)
    budget_used: Optional[Dict[str, Any]] = Field(default=None)
    budget_applied: Optional[Dict[str, Any]] = Field(default=None)
    applied_scores: Optional[List[QualityScore]] = Field(default=None)
    timestamp: Optional[Any] = Field(default=None)

    def model_post_init(self, __context: Any) -> None:
        """Populate memories from selected candidates if memories list is empty."""
        if not self.memories and self.selected:
            self.memories = [c.memory for c in self.selected]
        if not self.total_found:
            self.total_found = len(self.memories)
