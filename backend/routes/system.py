"""
System operations and health monitoring endpoints.
"""

from __future__ import annotations

from typing import Optional
from fastapi import APIRouter, Depends, Query, status
import structlog

from adaptive_memory.core.manager import MemoryQualityManager
from adaptive_memory.integrations.llm.base import LLMProvider
from adaptive_memory.integrations.search.base import SearchProvider
from adaptive_memory.integrations.speech.base import STTProvider, TTSProvider
from adaptive_memory.storage.sqlite import SQLiteStorage
from backend.dependencies import (
    get_llm,
    get_manager,
    get_search,
    get_storage,
    get_stt,
    get_tts,
)
from backend.schemas import HealthResponse, StatsResponse

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/api", tags=["System"])


@router.get("/health", response_model=HealthResponse)
async def health_check(
    storage: SQLiteStorage = Depends(get_storage),
    llm: Optional[LLMProvider] = Depends(get_llm),
    search: Optional[SearchProvider] = Depends(get_search),
    stt: Optional[STTProvider] = Depends(get_stt),
    tts: Optional[TTSProvider] = Depends(get_tts),
) -> HealthResponse:
    """Check storage availability and integration readiness."""
    storage_ok = False
    try:
        # Simple test query to ensure SQLite is responsive
        stats = await storage.get_stats("__health_check__")
        storage_ok = isinstance(stats, dict)
    except Exception as e:
        logger.error("Storage health check failed", error=str(e))
        storage_ok = False

    llm_ok = llm.is_available() if llm else False
    search_ok = search.is_available() if search else False
    speech_ok = (stt.is_available() if stt else False) or (tts.is_available() if tts else False)

    overall_status = "healthy" if storage_ok else "degraded"

    return HealthResponse(
        status=overall_status,
        storage_healthy=storage_ok,
        llm_available=llm_ok,
        search_available=search_ok,
        speech_available=speech_ok,
    )


@router.get("/stats", response_model=StatsResponse)
async def memory_stats(
    user_id: str = Query("default_user", description="Target user identifier"),
    manager: MemoryQualityManager = Depends(get_manager),
) -> StatsResponse:
    """Retrieve detailed memory counts, storage size, and average metrics for user."""
    stats = await manager.get_stats(user_id)
    return StatsResponse(user_id=user_id, stats=stats)
