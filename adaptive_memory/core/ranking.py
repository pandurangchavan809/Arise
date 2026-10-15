"""
Deterministic ranking engine for memory candidates.
Combines multidimensional quality scores, safety tier guarantees,
and context token efficiency to produce an optimal candidate ordering.
"""

from __future__ import annotations

from typing import List, Tuple
import structlog

from adaptive_memory.core.budget import EdgeBudgetController
from adaptive_memory.models import DecisionType, EdgeBudget, MemoryCandidate, QualityDecision, SafetyTier

logger = structlog.get_logger(__name__)


class MemoryRanker:
    """
    Ranks candidate memories by quality score, safety precedence, and token efficiency.
    """

    def __init__(self, score_tie_threshold: float = 0.05) -> None:
        self.tie_threshold = score_tie_threshold

    def _sorting_key(self, candidate: MemoryCandidate) -> Tuple[int, float, float]:
        """
        Multi-factor key for candidate ordering:
        1. Safety Tier boost for operational/high risk (>= T2 prioritized)
        2. Quality score total (higher is better)
        3. Token economy (shorter content preferred when scores are equivalent)
        """
        # Tier priority: T2, T3, T4 get a safety priority flag (1 vs 0)
        safety_priority = 1 if candidate.memory.risk_level >= SafetyTier.T2_OPERATIONAL else 0
        total_score = candidate.score.total

        # Invert token count so smaller content sorts first when quality is close
        tokens = EdgeBudgetController.estimate_tokens(candidate.memory.content)
        economy_factor = -float(tokens)

        return (safety_priority, total_score, economy_factor)

    def rank(
        self,
        candidates: List[MemoryCandidate],
        budget: EdgeBudget,
    ) -> Tuple[List[MemoryCandidate], List[MemoryCandidate]]:
        """
        Rank candidates and partition into selected and suppressed using the EdgeBudgetController.
        Returns:
            Tuple of (selected_candidates, suppressed_candidates)
        """
        if not candidates:
            return [], []

        # Filter out any candidates with unusable score or explicit suppression
        valid_candidates = []
        pre_suppressed = []

        for cand in candidates:
            if cand.decision.decision == DecisionType.SUPPRESSED:
                pre_suppressed.append(cand)
            elif cand.score.total < 0.15 and cand.memory.risk_level < SafetyTier.T2_OPERATIONAL:
                cand.decision = QualityDecision(
                    decision=DecisionType.SUPPRESSED,
                    reason=f"Quality score {cand.score.total:.3f} below minimum threshold 0.15"
                )
                pre_suppressed.append(cand)
            else:
                valid_candidates.append(cand)

        # Sort with safety precedence, quality score descending, token efficiency
        sorted_candidates = sorted(valid_candidates, key=self._sorting_key, reverse=True)

        # Apply Edge Budget Constraints
        budget_controller = EdgeBudgetController(budget)
        selected, budget_suppressed = budget_controller.apply(sorted_candidates)

        all_suppressed = pre_suppressed + budget_suppressed
        logger.debug(
            "Ranking complete",
            total_input=len(candidates),
            selected_count=len(selected),
            suppressed_count=len(all_suppressed)
        )
        return selected, all_suppressed
