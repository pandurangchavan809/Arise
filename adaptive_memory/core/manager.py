"""
Memory Quality Manager: The core deterministic, explainable memory middleware.
Orchestrates candidate retrieval, conflict resolution, multidimensional scoring,
ranking, safety tier guarantees, and edge budget enforcement.
"""

from __future__ import annotations

from datetime import datetime, timezone
import time
from typing import TYPE_CHECKING, Any, Dict, List, Optional
import structlog

from adaptive_memory.config import Settings, get_settings
from adaptive_memory.core.conflicts import ConflictDetector
from adaptive_memory.core.lifecycle import MemoryLifecycle
from adaptive_memory.core.quality import QualityScorer
from adaptive_memory.core.ranking import MemoryRanker
from adaptive_memory.models import (
    DecisionType,
    EdgeBudget,
    MemoryCandidate,
    MemoryRecord,
    MemoryStatus,
    MemoryType,
    OutcomeType,
    QualityDecision,
    RecallResult,
    SafetyTier,
)

if TYPE_CHECKING:
    from adaptive_memory.storage.interface import StorageBackend

logger = structlog.get_logger(__name__)


class MemoryQualityManager:
    """
    Deterministic Memory Quality Manager.
    Coordinates memory ingestion, recall pipelines, quality evaluation, and outcome calibration.
    """

    def __init__(
        self,
        storage: StorageBackend,
        config: Optional[Settings] = None,
        scorer: Optional[QualityScorer] = None,
        ranker: Optional[MemoryRanker] = None,
        conflict_detector: Optional[ConflictDetector] = None,
        lifecycle: Optional[MemoryLifecycle] = None,
    ) -> None:
        self.storage = storage
        self.config = config or get_settings()
        self.scorer = scorer or QualityScorer()
        self.ranker = ranker or MemoryRanker()
        self.conflict_detector = conflict_detector or ConflictDetector()
        self.lifecycle = lifecycle or MemoryLifecycle()
        self.alpha_utility = 0.3

    async def remember(
        self,
        content: str,
        user_id: str,
        memory_type: MemoryType = MemoryType.SESSION,
        source: str = "user",
        task_context: Optional[str] = None,
        confidence: float = 0.5,
        importance: float = 0.5,
        risk_level: SafetyTier = SafetyTier.T0_CASUAL,
        metadata: Optional[Dict[str, Any]] = None,
        expires_at: Optional[datetime] = None,
    ) -> MemoryRecord:
        """
        Store a new memory record with initial quality defaults and metadata.
        """
        now = datetime.now(timezone.utc)
        record = MemoryRecord(
            user_id=user_id,
            content=content.strip(),
            memory_type=memory_type,
            created_at=now,
            updated_at=now,
            expires_at=expires_at,
            source=source,
            task_context=task_context,
            confidence=max(0.0, min(1.0, confidence)),
            utility=0.5,
            importance=max(0.0, min(1.0, importance)),
            recency=1.0,
            risk_level=risk_level,
            status=MemoryStatus.ACTIVE,
            metadata=metadata or {},
        )

        stored_record = await self.storage.store(record)
        logger.info(
            "Memory remembered",
            memory_id=stored_record.id,
            user_id=user_id,
            type=stored_record.memory_type.value,
            risk=stored_record.risk_level.value,
        )
        return stored_record

    async def recall(
        self,
        query: str,
        user_id: str,
        budget: Optional[EdgeBudget] = None,
        situation: Optional[str] = None,
        memory_types: Optional[List[MemoryType]] = None,
    ) -> RecallResult:
        """
        Execute deterministic recall pipeline:
        1. Retrieve candidates from storage (FTS + metadata)
        2. Detect conflicts and resolve supersessions
        3. Score each candidate with multidimensional quality engine
        4. Apply safety tier constraints
        5. Rank candidates and enforce Edge Budget constraints
        6. Return RecallResult with selected and suppressed candidates
        """
        start_time = time.perf_counter()
        active_budget = budget or self.config.get_default_budget()

        # Step 1: Retrieve candidates from storage backend
        raw_records = await self.storage.search(
            query=query,
            user_id=user_id,
            memory_types=memory_types,
            limit=max(active_budget.max_memories * 4, 30),
            filters={"status": MemoryStatus.ACTIVE.value},
        )

        # Step 2: Detect conflicts among retrieved candidate records
        conflict_groups = self.conflict_detector.detect(raw_records)
        suppressed_by_conflict: Dict[str, str] = {}

        for group in conflict_groups:
            winner_id = group.resolution_id
            for mid in group.memory_ids:
                if mid != winner_id:
                    suppressed_by_conflict[mid] = (
                        f"Suppressed by conflict resolution in favor of {winner_id}. Reason: {group.reason}"
                    )

        # Step 3: Score each candidate with QualityScorer
        candidates: List[MemoryCandidate] = []
        for rec in raw_records:
            score = self.scorer.score(
                memory=rec,
                query=query,
                situation=situation,
                candidates=raw_records,
            )

            # Check if suppressed by conflict detector
            if rec.id in suppressed_by_conflict:
                cand = MemoryCandidate(
                    memory=rec,
                    score=score,
                    decision=QualityDecision(
                        decision=DecisionType.SUPPRESSED,
                        reason=suppressed_by_conflict[rec.id],
                        details={"conflict_group": True},
                    ),
                )
            else:
                cand = MemoryCandidate(
                    memory=rec,
                    score=score,
                    decision=QualityDecision(
                        decision=DecisionType.INCLUDED,
                        reason="Passed quality retrieval threshold",
                    ),
                )
            candidates.append(cand)

        # Step 4 & 5: Rank by quality score and apply Edge Budget constraints
        selected, suppressed = self.ranker.rank(candidates, active_budget)

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        logger.debug(
            "Recall completed",
            query=query,
            user_id=user_id,
            selected=len(selected),
            suppressed=len(suppressed),
            latency_ms=round(elapsed_ms, 2),
        )

        return RecallResult(
            query=query,
            candidates=candidates,
            selected=selected,
            suppressed=suppressed,
            budget_applied=active_budget,
            total_candidates=len(raw_records),
            timestamp=datetime.now(timezone.utc),
        )

    async def record_outcome(
        self,
        memory_ids: List[str],
        outcome: OutcomeType,
        user_id: str,
    ) -> None:
        """
        Calibrate utility using exponential moving update:
        U(t+1) = (1 - alpha) * U(t) + alpha * outcome_value
        where alpha = 0.3, helpful=+1, irrelevant=0, misleading=-1.
        The resulting utility is clamped into [0.0, 1.0].
        """
        outcome_val = outcome.value_score
        now = datetime.now(timezone.utc)

        for mid in memory_ids:
            record = await self.storage.get(mid)
            if not record or (user_id and record.user_id != user_id):
                continue

            current_u = record.utility
            # U(t+1) = (1 - alpha) * U(t) + alpha * outcome_val
            # where alpha = 0.3, helpful=+1, irrelevant=0, misleading=-1
            new_utility = (1.0 - self.alpha_utility) * current_u + self.alpha_utility * outcome_val
            clamped_utility = max(0.0, min(1.0, round(new_utility, 4)))

            await self.storage.update(
                mid,
                {
                    "utility": clamped_utility,
                    "updated_at": now.isoformat(),
                },
            )
            logger.info(
                "Utility updated from outcome",
                memory_id=mid,
                outcome=outcome.value,
                old_utility=current_u,
                new_utility=clamped_utility,
            )

    async def forget(self, memory_id: str, user_id: str) -> bool:
        """
        Permanently remove a memory record for the user.
        """
        record = await self.storage.get(memory_id)
        if not record or record.user_id != user_id:
            return False

        success = await self.storage.delete(memory_id)
        logger.info("Memory forgotten", memory_id=memory_id, user_id=user_id, deleted=success)
        return success

    async def archive(self, memory_id: str, user_id: str) -> MemoryRecord:
        """
        Archive a memory record without deleting it.
        """
        record = await self.storage.get(memory_id)
        if not record or record.user_id != user_id:
            raise ValueError(f"Memory {memory_id} not found or user mismatch")

        updated = await self.lifecycle.update_status(memory_id, MemoryStatus.ARCHIVED, self.storage)
        return updated

    async def get_stats(self, user_id: str) -> Dict[str, Any]:
        """
        Retrieve memory statistics for a user.
        """
        stats = await self.storage.get_stats(user_id)
        stats["manager_version"] = "0.1.0"
        return stats
