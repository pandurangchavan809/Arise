"""
Unit tests for QualityScorer: relevance, utility, confidence, recency decay, and conflict risk.
"""

from datetime import datetime, timedelta, timezone
import pytest

from adaptive_memory.core.quality import QualityScorer
from adaptive_memory.models import MemoryRecord, MemoryType, SafetyTier


@pytest.fixture
def scorer() -> QualityScorer:
    return QualityScorer()


def test_score_weights_sum(scorer: QualityScorer):
    """Test that all scoring weights sum up to 1.0 (positive weights + conflict penalty weight)."""
    positive_sum = scorer.w_relevance + scorer.w_utility + scorer.w_confidence + scorer.w_recency
    total_weights = positive_sum + scorer.w_conflict
    assert round(positive_sum, 2) == 0.90
    assert round(total_weights, 2) == 1.00
    assert scorer.w_relevance == 0.30
    assert scorer.w_utility == 0.25
    assert scorer.w_confidence == 0.20
    assert scorer.w_recency == 0.15
    assert scorer.w_conflict == 0.10


def test_score_computation(scorer: QualityScorer):
    """Test complete end-to-end score computation returning QualityScore object."""
    mem = MemoryRecord(
        user_id="user_1",
        content="Deploying FastAPI applications using Docker and Uvicorn",
        memory_type=MemoryType.LONG_TERM,
        confidence=0.8,
        utility=0.7,
        source="user",
    )
    score = scorer.score(memory=mem, query="FastAPI Docker deployment")

    assert score is not None
    assert 0.0 <= score.total <= 1.0
    assert 0.0 <= score.relevance <= 1.0
    assert score.utility == 0.7
    assert 0.0 <= score.confidence <= 1.0
    assert 0.0 <= score.recency <= 1.0
    assert score.explanation is not None
    assert "formula" in score.explanation
    assert score.explanation["total"] == score.total


def test_relevance_high_match(scorer: QualityScorer):
    """Test that query matching memory tokens produces high relevance score (>0.7)."""
    mem = MemoryRecord(
        user_id="user_1",
        content="PostgreSQL database replication with streaming read replicas",
        memory_type=MemoryType.LONG_TERM,
    )
    rel_high = scorer._compute_relevance(mem, query="PostgreSQL replication read replicas")
    assert rel_high >= 0.70


def test_relevance_low_match(scorer: QualityScorer):
    """Test that query with disjoint tokens produces low or zero relevance score."""
    mem = MemoryRecord(
        user_id="user_1",
        content="Kubernetes pod autoscaling using Prometheus metrics",
        memory_type=MemoryType.LONG_TERM,
    )
    rel_low = scorer._compute_relevance(mem, query="baking chocolate cake recipes")
    assert rel_low == 0.0


def test_utility_scoring(scorer: QualityScorer):
    """Test that utility scoring correctly bounds values in [0, 1]."""
    mem_high = MemoryRecord(user_id="u1", content="Text", utility=0.95)
    mem_low = MemoryRecord(user_id="u1", content="Text", utility=0.1)

    assert scorer._compute_utility(mem_high) == 0.95
    assert scorer._compute_utility(mem_low) == 0.1


def test_confidence_scoring(scorer: QualityScorer):
    """Test source weighting on confidence: user (1.0) > system (0.95) > tool (0.9) > agent (0.85)."""
    mem_user = MemoryRecord(user_id="u1", content="Pref", confidence=0.8, source="user")
    mem_system = MemoryRecord(user_id="u1", content="Pref", confidence=0.8, source="system")
    mem_tool = MemoryRecord(user_id="u1", content="Pref", confidence=0.8, source="tool")
    mem_agent = MemoryRecord(user_id="u1", content="Pref", confidence=0.8, source="agent")

    conf_user = scorer._compute_confidence(mem_user)
    conf_system = scorer._compute_confidence(mem_system)
    conf_tool = scorer._compute_confidence(mem_tool)
    conf_agent = scorer._compute_confidence(mem_agent)

    assert conf_user == 0.8
    assert conf_system == round(0.8 * 0.95, 4)
    assert conf_tool == round(0.8 * 0.90, 4)
    assert conf_agent == round(0.8 * 0.85, 4)
    assert conf_user > conf_system > conf_tool > conf_agent


def test_recency_decay(scorer: QualityScorer):
    """Test exponential recency decay over time (new > 1 day old > 30 days old)."""
    now = datetime.now(timezone.utc)

    mem_now = MemoryRecord(user_id="u1", content="T", updated_at=now)
    mem_1d = MemoryRecord(user_id="u1", content="T", updated_at=now - timedelta(days=1))
    mem_30d = MemoryRecord(user_id="u1", content="T", updated_at=now - timedelta(days=30))

    rec_now = scorer._compute_recency(mem_now)
    rec_1d = scorer._compute_recency(mem_1d)
    rec_30d = scorer._compute_recency(mem_30d)

    assert rec_now > rec_1d > rec_30d
    assert rec_now >= 0.99
    assert rec_30d < 0.05


def test_conflict_risk_detection(scorer: QualityScorer):
    """Test conflict risk score computation when a candidate conflicts with another."""
    now = datetime.now(timezone.utc)
    mem_older = MemoryRecord(
        user_id="u1",
        content="Primary cloud deployment region is us-east-1 northern virginia",
        confidence=0.7,
        updated_at=now - timedelta(days=2),
    )
    mem_newer = MemoryRecord(
        user_id="u1",
        content="Primary cloud deployment region is us-west-2 oregon aws",
        confidence=0.9,
        updated_at=now,
    )

    risk_older = scorer._compute_conflict_risk(mem_older, candidates=[mem_older, mem_newer])
    assert risk_older >= 0.5

    # With explicit conflict in metadata
    mem_explicit = MemoryRecord(
        user_id="u1",
        content="Target database port is 5432",
        metadata={"conflicts_with": mem_older.id},
    )
    risk_explicit = scorer._compute_conflict_risk(mem_older, candidates=[mem_older, mem_explicit])
    assert risk_explicit >= 0.9


def test_total_score_formula(scorer: QualityScorer):
    """Test the exact mathematical composite formula:
    Q = 0.30*rel + 0.25*util + 0.20*conf + 0.15*rec - 0.10*conflict
    """
    rel = 0.8
    util = 0.6
    conf = 0.9
    rec = 0.5
    conflict = 0.2

    expected = (
        0.30 * rel
        + 0.25 * util
        + 0.20 * conf
        + 0.15 * rec
        - 0.10 * conflict
    )
    expected_rounded = round(expected, 4)

    calculated = scorer._compute_total(
        relevance=rel,
        utility=util,
        confidence=conf,
        recency=rec,
        conflict_risk=conflict,
    )

    assert calculated == expected_rounded
    assert 0.0 <= calculated <= 1.0
