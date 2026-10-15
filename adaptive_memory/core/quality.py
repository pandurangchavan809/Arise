"""
Deterministic and explainable Memory Quality Scoring engine.
Calculates multidimensional quality metrics based on relevance, utility, confidence,
recency decay, and conflict risk.
"""

from __future__ import annotations

from datetime import datetime, timezone
import math
import re
from typing import Any, Dict, List, Optional, Set

import structlog

from adaptive_memory.models import MemoryRecord, QualityScore

logger = structlog.get_logger(__name__)


# Common English stop words to filter during keyword extraction
STOP_WORDS: Set[str] = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are",
    "aren't", "as", "at", "be", "because", "been", "before", "being", "below", "between", "both",
    "but", "by", "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't",
    "doing", "don't", "down", "during", "each", "few", "for", "from", "further", "had", "hadn't",
    "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here",
    "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll",
    "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's",
    "me", "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off", "on",
    "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own",
    "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some",
    "such", "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then",
    "there", "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this",
    "those", "through", "to", "too", "under", "until", "up", "very", "was", "wasn't", "we",
    "we'd", "we'll", "we're", "we've", "were", "weren't", "what", "what's", "when", "when's",
    "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with",
    "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours",
    "yourself", "yourselves"
}


class QualityScorer:
    """
    Computes explainable, deterministic quality scores for memory candidates.
    Formula: Q = 0.30*relevance + 0.25*utility + 0.20*confidence + 0.15*recency - 0.10*conflict_risk
    """

    def __init__(
        self,
        weight_relevance: float = 0.30,
        weight_utility: float = 0.25,
        weight_confidence: float = 0.20,
        weight_recency: float = 0.15,
        weight_conflict: float = 0.10,
        recency_lambda: float = 0.01,
    ) -> None:
        self.w_relevance = weight_relevance
        self.w_utility = weight_utility
        self.w_confidence = weight_confidence
        self.w_recency = weight_recency
        self.w_conflict = weight_conflict
        self.recency_lambda = recency_lambda

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        """Tokenize string into alphanumeric terms excluding stop words."""
        raw_tokens = re.findall(r"\b[a-zA-Z0-9_\-]{2,}\b", text.lower())
        return [t for t in raw_tokens if t not in STOP_WORDS]

    def _compute_relevance(self, memory: MemoryRecord, query: str, situation: Optional[str] = None) -> float:
        """
        Compute lexical and contextual relevance between query/situation and memory content.
        Uses Jaccard similarity and token recall metrics.
        """
        if not query and not situation:
            return 0.5  # Neutral default when no query provided

        query_tokens = set(self._tokenize(query or ""))
        if situation:
            query_tokens.update(self._tokenize(situation))

        if not query_tokens:
            return 0.5

        content_tokens = set(self._tokenize(memory.content))
        if memory.task_context:
            content_tokens.update(self._tokenize(memory.task_context))

        if not content_tokens:
            return 0.0

        intersection = query_tokens.intersection(content_tokens)
        if not intersection:
            # Check for substring match in content
            q_clean = query.lower().strip()
            if q_clean and q_clean in memory.content.lower():
                return 0.8
            return 0.0

        # Weighted combination of token coverage of query and Jaccard overlap
        query_coverage = len(intersection) / len(query_tokens)
        jaccard = len(intersection) / len(query_tokens.union(content_tokens))

        score = (0.7 * query_coverage) + (0.3 * jaccard)
        return min(max(score, 0.0), 1.0)

    def _compute_utility(self, memory: MemoryRecord) -> float:
        """Utility from empirical outcome feedback, bounded in [0, 1]."""
        return min(max(float(memory.utility), 0.0), 1.0)

    def _compute_confidence(self, memory: MemoryRecord) -> float:
        """Compute memory confidence, weighting origin and explicit flag."""
        base_confidence = min(max(float(memory.confidence), 0.0), 1.0)

        # Source modifiers
        multiplier = 1.0
        if memory.source == "user":
            multiplier = 1.0
        elif memory.source == "system":
            multiplier = 0.95
        elif memory.source == "tool":
            multiplier = 0.90
        elif memory.source == "agent":
            multiplier = 0.85

        return min(max(base_confidence * multiplier, 0.0), 1.0)

    def _compute_recency(self, memory: MemoryRecord) -> float:
        """
        Compute exponential recency decay:
        recency = exp(-lambda * hours_since_update) where lambda = 0.01.
        """
        now = datetime.now(timezone.utc)
        ref_time = memory.updated_at or memory.created_at

        # Ensure tz-aware
        if ref_time.tzinfo is None:
            ref_time = ref_time.replace(tzinfo=timezone.utc)

        delta = now - ref_time
        hours = max(delta.total_seconds() / 3600.0, 0.0)

        decayed = math.exp(-self.recency_lambda * hours)
        return min(max(decayed, 0.0), 1.0)

    def _compute_conflict_risk(
        self,
        memory: MemoryRecord,
        candidates: Optional[List[MemoryRecord]] = None,
    ) -> float:
        """
        Compute conflict penalty if this memory conflicts with higher-confidence
        or more recent candidates.
        """
        if not candidates:
            return 0.0

        conflict_score = 0.0
        mem_tokens = set(self._tokenize(memory.content))

        for other in candidates:
            if other.id == memory.id:
                continue

            other_tokens = set(self._tokenize(other.content))
            overlap = mem_tokens.intersection(other_tokens)
            # High overlap between different memories on the same user may indicate conflicting statements
            if len(overlap) >= 3 and (len(overlap) / max(len(mem_tokens), 1)) > 0.5:
                # If other is newer and has higher or equal confidence, this one risks conflict
                if other.updated_at > memory.updated_at and other.confidence >= memory.confidence:
                    conflict_score = max(conflict_score, 0.5)
                # If explicitly marked conflicting in metadata
                if other.metadata.get("conflicts_with") == memory.id:
                    conflict_score = max(conflict_score, 0.9)

        return min(conflict_score, 1.0)

    def _compute_total(
        self,
        relevance: float,
        utility: float,
        confidence: float,
        recency: float,
        conflict_risk: float,
    ) -> float:
        """Calculate weighted composite score."""
        raw_total = (
            self.w_relevance * relevance
            + self.w_utility * utility
            + self.w_confidence * confidence
            + self.w_recency * recency
            - self.w_conflict * conflict_risk
        )
        return round(min(max(raw_total, 0.0), 1.0), 4)

    def score(
        self,
        memory: MemoryRecord,
        query: str,
        situation: Optional[str] = None,
        candidates: Optional[List[MemoryRecord]] = None,
    ) -> QualityScore:
        """Generate deterministic quality score with full explainability trace."""
        relevance = round(self._compute_relevance(memory, query, situation), 4)
        utility = round(self._compute_utility(memory), 4)
        confidence = round(self._compute_confidence(memory), 4)
        recency = round(self._compute_recency(memory), 4)
        conflict_risk = round(self._compute_conflict_risk(memory, candidates), 4)

        total = self._compute_total(relevance, utility, confidence, recency, conflict_risk)

        explanation = {
            "formula": "0.30*relevance + 0.25*utility + 0.20*confidence + 0.15*recency - 0.10*conflict_risk",
            "weights": {
                "relevance": self.w_relevance,
                "utility": self.w_utility,
                "confidence": self.w_confidence,
                "recency": self.w_recency,
                "conflict_risk": self.w_conflict,
            },
            "values": {
                "relevance": relevance,
                "utility": utility,
                "confidence": confidence,
                "recency": recency,
                "conflict_risk": conflict_risk,
            },
            "total": total,
        }

        return QualityScore(
            relevance=relevance,
            utility=utility,
            confidence=confidence,
            recency=recency,
            conflict_risk=conflict_risk,
            total=total,
            explanation=explanation,
        )
