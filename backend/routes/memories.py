"""
CRUD endpoints for memory entities.
Provides operations to create, list, inspect, patch, and delete memory records.
"""

from __future__ import annotations

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
import structlog

from adaptive_memory.core.manager import MemoryQualityManager
from adaptive_memory.models import MemoryRecord, MemoryStatus, MemoryType, SafetyTier
from adaptive_memory.storage.sqlite import SQLiteStorage
from backend.dependencies import get_manager, get_storage
from backend.schemas import (
    CreateMemoryRequest,
    ListMemoriesResponse,
    MemoryResponse,
    UpdateMemoryRequest,
)

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/api/memories", tags=["Memories"])


@router.post("", response_model=MemoryResponse, status_code=status.HTTP_201_CREATED)
async def create_memory(
    payload: CreateMemoryRequest,
    manager: MemoryQualityManager = Depends(get_manager),
) -> MemoryResponse:
    """Create a new memory record managed by the quality engine."""
    try:
        record = await manager.remember(
            content=payload.content,
            user_id=payload.user_id,
            memory_type=payload.memory_type,
            source=payload.source,
            task_context=payload.task_context,
            confidence=payload.confidence,
            importance=payload.importance,
            risk_level=payload.risk_level,
            metadata=payload.metadata,
            expires_at=payload.expires_at,
        )
        return MemoryResponse(memory=record)
    except Exception as e:
        logger.error("Failed to create memory", error=str(e), user_id=payload.user_id)
        raise HTTPException(status_code=500, detail=f"Failed to create memory: {e}")


@router.get("", response_model=ListMemoriesResponse)
async def list_memories(
    user_id: Optional[str] = Query(None, description="User identifier filter"),
    memory_type: Optional[MemoryType] = Query(None, description="Memory type filter"),
    status_filter: Optional[MemoryStatus] = Query(None, alias="status", description="Status filter"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    storage: SQLiteStorage = Depends(get_storage),
) -> ListMemoriesResponse:
    """List memory records matching optional user, type, and status filters."""
    filters = {}
    if status_filter:
        filters["status"] = status_filter.value

    types = [memory_type] if memory_type else None
    records = await storage.search(
        query="",
        user_id=user_id or "",
        memory_types=types,
        limit=limit,
        filters=filters,
    )
    return ListMemoriesResponse(
        memories=records,
        total=len(records),
        user_id=user_id,
    )


@router.get("/{memory_id}", response_model=MemoryResponse)
async def get_memory(
    memory_id: str,
    storage: SQLiteStorage = Depends(get_storage),
) -> MemoryResponse:
    """Retrieve an existing memory record by its unique ID."""
    record = await storage.get(memory_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Memory record with ID '{memory_id}' not found",
        )
    return MemoryResponse(memory=record)


@router.patch("/{memory_id}", response_model=MemoryResponse)
async def update_memory(
    memory_id: str,
    payload: UpdateMemoryRequest,
    storage: SQLiteStorage = Depends(get_storage),
) -> MemoryResponse:
    """Update fields of an existing memory record."""
    record = await storage.get(memory_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Memory record with ID '{memory_id}' not found",
        )

    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        return MemoryResponse(memory=record)

    # Convert Enums to string values
    if "risk_level" in updates and updates["risk_level"]:
        updates["risk_level"] = updates["risk_level"].value
    if "status" in updates and updates["status"]:
        updates["status"] = updates["status"].value

    try:
        updated = await storage.update(memory_id, updates)
        return MemoryResponse(memory=updated)
    except Exception as e:
        logger.error("Failed to update memory", memory_id=memory_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to update memory: {e}")


@router.delete("/{memory_id}", status_code=status.HTTP_200_OK)
async def delete_memory(
    memory_id: str,
    storage: SQLiteStorage = Depends(get_storage),
) -> dict:
    """Permanently delete a memory record."""
    deleted = await storage.delete(memory_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Memory record with ID '{memory_id}' not found or already deleted",
        )
    return {"status": "success", "deleted_id": memory_id}
