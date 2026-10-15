"""
Memory Operations endpoints.
Exposes recall with quality scoring, outcome calibration, forgetting, archiving,
and type-specific listings for session, long-term, experience, and prospective tiers.
"""

from __future__ import annotations

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
import structlog

from adaptive_memory.core.manager import MemoryQualityManager
from adaptive_memory.models import EdgeBudget, MemoryRecord, MemoryType
from adaptive_memory.storage.sqlite import SQLiteStorage
from backend.dependencies import get_config, get_manager, get_storage
from backend.schemas import (
    ArchiveRequest,
    ForgetRequest,
    ListMemoriesResponse,
    MemoryResponse,
    OutcomeRequest,
    PromoteRequest,
    RecallRequest,
    RecallResponse,
)

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/api/memory", tags=["Memory Operations"])


@router.post("/recall", response_model=RecallResponse)
async def recall_memories(
    payload: RecallRequest,
    manager: MemoryQualityManager = Depends(get_manager),
) -> RecallResponse:
    """
    Execute deterministic recall pipeline:
    Filters, detects conflicts, scores quality, enforces safety tiers, and applies edge budget.
    """
    settings = get_config()
    budget = EdgeBudget(
        max_memories=payload.max_memories or settings.max_memories,
        max_context_tokens=payload.max_tokens or settings.max_context_tokens,
        max_latency_ms=settings.max_latency_ms,
        max_storage_bytes=settings.max_storage_bytes,
    )

    try:
        result = await manager.recall(
            query=payload.query,
            user_id=payload.user_id,
            budget=budget,
            situation=payload.situation,
            memory_types=payload.memory_types,
        )
        return RecallResponse(result=result)
    except Exception as e:
        logger.error("Recall operation failed", query=payload.query, error=str(e))
        raise HTTPException(status_code=500, detail=f"Recall failed: {e}")


@router.post("/outcome", status_code=status.HTTP_200_OK)
async def record_outcome(
    payload: OutcomeRequest,
    manager: MemoryQualityManager = Depends(get_manager),
) -> dict:
    """
    Submit outcome feedback to update utility scores using exponential smoothing:
    U(t+1) = (1 - alpha) * U(t) + alpha * outcome_val.
    """
    try:
        await manager.record_outcome(
            memory_ids=payload.memory_ids,
            outcome=payload.outcome,
            user_id=payload.user_id,
        )
        return {
            "status": "recorded",
            "memory_ids": payload.memory_ids,
            "outcome": payload.outcome.value,
        }
    except Exception as e:
        logger.error("Failed to record outcome feedback", error=str(e))
        raise HTTPException(status_code=500, detail=f"Outcome feedback failed: {e}")


@router.post("/forget", status_code=status.HTTP_200_OK)
async def forget_memory(
    payload: ForgetRequest,
    manager: MemoryQualityManager = Depends(get_manager),
) -> dict:
    """Explicitly delete memory record for user."""
    success = await manager.forget(payload.memory_id, payload.user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Memory {payload.memory_id} not found or user mismatch",
        )
    return {"status": "forgotten", "memory_id": payload.memory_id}


@router.post("/archive", response_model=MemoryResponse)
async def archive_memory(
    payload: ArchiveRequest,
    manager: MemoryQualityManager = Depends(get_manager),
) -> MemoryResponse:
    """Archive a memory record without permanently deleting it."""
    try:
        record = await manager.archive(payload.memory_id, payload.user_id)
        return MemoryResponse(memory=record)
    except Exception as e:
        logger.error("Failed to archive memory", memory_id=payload.memory_id, error=str(e))
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/promote", response_model=MemoryResponse)
async def promote_memory(
    payload: PromoteRequest,
    storage: SQLiteStorage = Depends(get_storage),
) -> MemoryResponse:
    """Promote memory to a new tier (e.g. SESSION to LONG_TERM)."""
    try:
        from adaptive_memory.core.lifecycle import MemoryLifecycle
        record = await MemoryLifecycle.promote(payload.memory_id, payload.target_type, storage)
        return MemoryResponse(memory=record)
    except Exception as e:
        logger.error("Failed to promote memory", memory_id=payload.memory_id, error=str(e))
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/session", response_model=ListMemoriesResponse)
async def list_session_memories(
    user_id: str = Query(..., description="User ID"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    storage: SQLiteStorage = Depends(get_storage),
) -> ListMemoriesResponse:
    """List session-scoped memories."""
    records = await storage.list_by_type(user_id, MemoryType.SESSION, limit=limit, offset=offset)
    return ListMemoriesResponse(memories=records, total=len(records), user_id=user_id)


@router.get("/long-term", response_model=ListMemoriesResponse)
async def list_long_term_memories(
    user_id: str = Query(..., description="User ID"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    storage: SQLiteStorage = Depends(get_storage),
) -> ListMemoriesResponse:
    """List permanent long-term memories."""
    records = await storage.list_by_type(user_id, MemoryType.LONG_TERM, limit=limit, offset=offset)
    return ListMemoriesResponse(memories=records, total=len(records), user_id=user_id)


@router.get("/experience", response_model=ListMemoriesResponse)
async def list_experience_memories(
    user_id: str = Query(..., description="User ID"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    storage: SQLiteStorage = Depends(get_storage),
) -> ListMemoriesResponse:
    """List experience memories tracking procedural trials and outcomes."""
    records = await storage.list_by_type(user_id, MemoryType.EXPERIENCE, limit=limit, offset=offset)
    return ListMemoriesResponse(memories=records, total=len(records), user_id=user_id)


@router.get("/prospective", response_model=ListMemoriesResponse)
async def list_prospective_memories(
    user_id: str = Query(..., description="User ID"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    storage: SQLiteStorage = Depends(get_storage),
) -> ListMemoriesResponse:
    """List prospective memories representing reminders, scheduled tasks, and intentions."""
    records = await storage.list_by_type(user_id, MemoryType.PROSPECTIVE, limit=limit, offset=offset)
    return ListMemoriesResponse(memories=records, total=len(records), user_id=user_id)
