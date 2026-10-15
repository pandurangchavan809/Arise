"""
Core Pydantic models and enumerations for Adaptive Memory Runtime.
Defines schemas for memory records, quality scoring, candidates, decisions, and edge budgets.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid

from pydantic import BaseModel, Field, field_validator


class MemoryType(str, Enum):
    """Classification of memory lifespan and function."""
    SESSION = "session"
    LONG_TERM = "long_term"
    EXPERIENCE = "experience"
    PROSPECTIVE = "prospective"


class MemoryStatus(str, Enum):
    """Operational status of a memory record."""
    ACTIVE = "active"
    ARCHIVED = "archived"
    EXPIRED = "expired"
    SUPPRESSED = "suppressed"


class SafetyTier(str, Enum):
    """Safety and risk categorization tier."""
    T0_CASUAL = "T0"
    T1_PERSONAL = "T1"
    T2_OPERATIONAL = "T2"
    T3_SENSITIVE = "T3"
    T4_HIGH_RISK = "T4"

    @property
    def level(self) -> int:
        """Numeric rank for safety comparison."""
        mapping = {
            SafetyTier.T0_CASUAL: 0,
            SafetyTier.T1_PERSONAL: 1,
            SafetyTier.T2_OPERATIONAL: 2,
            SafetyTier.T3_SENSITIVE: 3,
            SafetyTier.T4_HIGH_RISK: 4,
        }
        return mapping[self]

    def __ge__(self, other: SafetyTier) -> bool:
        if isinstance(other, SafetyTier):
            return self.level >= other.level
        return NotImplemented

    def __gt__(self, other: SafetyTier) -> bool:
        if isinstance(other, SafetyTier):
            return self.level > other.level
        return NotImplemented

    def __le__(self, other: SafetyTier) -> bool:
        if isinstance(other, SafetyTier):
            return self.level <= other.level
        return NotImplemented

    def __lt__(self, other: SafetyTier) -> bool:
        if isinstance(other, SafetyTier):
            return self.level < other.level
        return NotImplemented


class OutcomeType(str, Enum):
    """Outcome feedback for memory utility calibration."""
    HELPFUL = "helpful"
    IRRELEVANT = "irrelevant"
    MISLEADING = "misleading"

    @property
    def value_score(self) -> float:
        """Outcome numerical value for exponential smoothing update."""
        mapping = {
            OutcomeType.HELPFUL: 1.0,
            OutcomeType.IRRELEVANT: 0.0,
            OutcomeType.MISLEADING: -1.0,
        }
        return mapping[self]


class DecisionType(str, Enum):
    """Decision state for candidate memory inclusion in recall context."""
    INCLUDED = "included"
    SUPPRESSED = "suppressed"


class MemoryRecord(BaseModel):
    """Canonical memory record entity with tracking and quality parameters."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = Field(..., description="Unique identifier of user/agent owning this memory")
    content: str = Field(..., description="Text content of the memory")
    memory_type: MemoryType = Field(default=MemoryType.SESSION)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = Field(default=None, description="Optional expiry timestamp")
    source: str = Field(default="user", description="Origin of memory e.g., user, conversation, agent, tool")
    task_context: Optional[str] = Field(default=None, description="Task or domain context when stored")
    confidence: float = Field(default=0.5, ge=0.0, le=1.0, description="Confidence in accuracy [0, 1]")
    utility: float = Field(default=0.5, ge=0.0, le=1.0, description="Empirical utility rating [0, 1]")
    importance: float = Field(default=0.5, ge=0.0, le=1.0, description="Inherent importance [0, 1]")
    recency: float = Field(default=1.0, ge=0.0, le=1.0, description="Calculated recency score [0, 1]")
    risk_level: SafetyTier = Field(default=SafetyTier.T0_CASUAL)
    status: MemoryStatus = Field(default=MemoryStatus.ACTIVE)
    embedding: Optional[List[float]] = Field(default=None, description="Optional vector embedding representation")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary structured metadata")

    @field_validator("created_at", "updated_at", mode="before")
    @classmethod
    def ensure_tz_aware(cls, v: Any) -> datetime:
        if isinstance(v, str):
            dt = datetime.fromisoformat(v)
            if dt.tzinfo is None:
                return dt.replace(tzinfo=timezone.utc)
            return dt
        if isinstance(v, datetime) and v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v

    @field_validator("expires_at", mode="before")
    @classmethod
    def ensure_expires_tz_aware(cls, v: Any) -> Optional[datetime]:
        if v is None:
            return None
        if isinstance(v, str):
            dt = datetime.fromisoformat(v)
            if dt.tzinfo is None:
                return dt.replace(tzinfo=timezone.utc)
            return dt
        if isinstance(v, datetime) and v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v


class QualityScore(BaseModel):
    """Breakdown of deterministic quality dimensions and total score."""
    relevance: float = Field(default=0.0, description="Query-content semantic/keyword relevance [0, 1]")
    utility: float = Field(default=0.0, description="Historical usefulness [0, 1]")
    confidence: float = Field(default=0.0, description="Memory certainty [0, 1]")
    recency: float = Field(default=0.0, description="Time-decay factor [0, 1]")
    conflict_risk: float = Field(default=0.0, description="Inter-memory conflict penalty [0, 1]")
    total: float = Field(default=0.0, description="Composite weighted quality score")
    explanation: Optional[Dict[str, Any]] = Field(default=None, description="Explainability breakdown of weights and factors")


class QualityDecision(BaseModel):
    """Quality manager inclusion or suppression decision."""
    decision: DecisionType = Field(default=DecisionType.INCLUDED)
    reason: str = Field(..., description="Explainable reason for decision")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Extra context supporting the decision")


class MemoryCandidate(BaseModel):
    """Candidate memory evaluated through the quality evaluation pipeline."""
    memory: MemoryRecord
    score: QualityScore
    decision: QualityDecision


class EdgeBudget(BaseModel):
    """Edge budget constraints controlling recall size, token limits, latency, and footprint."""
    max_memories: int = Field(default=10, ge=1, description="Max memories to return in context")
    max_context_tokens: int = Field(default=2000, ge=1, description="Max tokens allowed for memory injection")
    max_latency_ms: int = Field(default=100, ge=1, description="Budget retrieval target latency ceiling in ms")
    max_storage_bytes: int = Field(default=104857600, ge=1024, description="Local storage limit (100MB default)")


class RecallResult(BaseModel):
    """Structured recall result containing selected memories, suppressed candidates, and budget metadata."""
    query: str
    candidates: List[MemoryCandidate]
    selected: List[MemoryCandidate]
    suppressed: List[MemoryCandidate] = Field(default_factory=list)
    budget_applied: EdgeBudget
    total_candidates: int
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
