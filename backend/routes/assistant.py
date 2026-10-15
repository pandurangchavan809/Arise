"""
Assistant endpoints: Memory-augmented chat, web search, and voice STT/TTS processing.
"""

from __future__ import annotations

import base64
import re
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Response, status
import structlog

from adaptive_memory.core.manager import MemoryQualityManager
from adaptive_memory.integrations.llm.base import LLMProvider
from adaptive_memory.integrations.search.base import SearchProvider
from adaptive_memory.integrations.speech.base import STTProvider, TTSProvider
from adaptive_memory.models import MemoryCandidate, MemoryRecord, MemoryType, SafetyTier
from backend.dependencies import (
    get_llm,
    get_manager,
    get_search,
    get_stt,
    get_tts,
)
from backend.schemas import (
    ChatRequest,
    ChatResponse,
    SearchRequest,
    SpeakRequest,
    TranscribeRequest,
)

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/api", tags=["Assistant & Multimodal"])


def extract_potential_memories(user_message: str, assistant_reply: str) -> List[Dict[str, Any]]:
    """
    Heuristic rule-based memory extractor for conversational statements.
    Detects personal preferences, rules, declarations, and facts.
    """
    extracted = []
    patterns = [
        (r"(?:i prefer|i like|i love|my preference is)\s+(.*)", MemoryType.LONG_TERM, SafetyTier.T1_PERSONAL),
        (r"(?:i live in|i work at|my job is|my name is)\s+(.*)", MemoryType.LONG_TERM, SafetyTier.T1_PERSONAL),
        (r"(?:remember that|always remember|don't forget that)\s+(.*)", MemoryType.LONG_TERM, SafetyTier.T2_OPERATIONAL),
        (r"(?:never|do not|don't ever)\s+(.*)", MemoryType.LONG_TERM, SafetyTier.T2_OPERATIONAL),
        (r"(?:remind me to|schedule|i need to)\s+(.*)", MemoryType.PROSPECTIVE, SafetyTier.T1_PERSONAL),
    ]

    for line in user_message.split("."):
        line_clean = line.strip()
        for pat, m_type, s_tier in patterns:
            match = re.search(pat, line_clean, re.IGNORECASE)
            if match:
                extracted.append({
                    "content": line_clean,
                    "memory_type": m_type,
                    "risk_level": s_tier,
                    "confidence": 0.85,
                })
                break

    return extracted


@router.post("/chat", response_model=ChatResponse)
async def chat_assistant(
    payload: ChatRequest,
    manager: MemoryQualityManager = Depends(get_manager),
    llm: Optional[LLMProvider] = Depends(get_llm),
    search: Optional[SearchProvider] = Depends(get_search),
) -> ChatResponse:
    """
    Augmented chat pipeline:
    1. Recall relevant memories
    2. Build context with trusted memories
    3. Optionally search web via Tavily
    4. Send to LLM
    5. Extract and store new memories from conversation
    6. Return response + memory quality info
    """
    selected_memories: List[MemoryCandidate] = []
    search_results_data: List[Dict[str, Any]] = []

    # Step 1: Recall relevant memories
    if payload.use_memory:
        try:
            recall_res = await manager.recall(
                query=payload.message,
                user_id=payload.user_id,
                situation=f"session:{payload.session_id}" if payload.session_id else None,
            )
            selected_memories = recall_res.selected
        except Exception as e:
            logger.warning("Memory recall step encountered error", error=str(e))

    # Step 2: Build context block
    system_prompt = (
        "You are an intelligent assistant powered by Adaptive Memory Runtime.\n"
        "Use the provided context and memories to inform your answer truthfully.\n"
    )

    if selected_memories:
        memory_lines = [
            f"- [{c.memory.memory_type.value}] (Confidence: {c.score.confidence:.2f}, Safety: {c.memory.risk_level.value}): {c.memory.content}"
            for c in selected_memories
        ]
        system_prompt += "\nRelevant Memories from User History:\n" + "\n".join(memory_lines) + "\n"

    # Step 3: Optional Tavily web search
    if payload.use_search and search and search.is_available():
        try:
            s_results = await search.search(payload.message, max_results=3)
            search_results_data = [res.model_dump() for res in s_results]
            if s_results:
                search_lines = [f"- [{r.title}] ({r.url}): {r.content}" for r in s_results]
                system_prompt += "\nReal-Time Web Search Results:\n" + "\n".join(search_lines) + "\n"
        except Exception as e:
            logger.warning("Web search step encountered error", error=str(e))

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": payload.message},
    ]

    # Step 4: Send to LLM
    assistant_reply = ""
    if llm and llm.is_available():
        try:
            assistant_reply = await llm.chat(messages=messages, temperature=0.7)
        except Exception as e:
            logger.error("LLM inference call failed", error=str(e))
            assistant_reply = (
                f"LLM request error: {e}. "
                f"However, {len(selected_memories)} memories were successfully retrieved from runtime."
            )
    else:
        # Informative fallback when no LLM API key is provided
        mem_summary = f"{len(selected_memories)} relevant memories retrieved" if selected_memories else "No prior memories matched"
        assistant_reply = (
            f"[Nebius API Key not configured]. Memory runtime active: {mem_summary}. "
            f"Prompt received: '{payload.message}'."
        )

    # Step 5: Extract and store new memories
    extracted_records: List[MemoryRecord] = []
    candidates_to_store = extract_potential_memories(payload.message, assistant_reply)

    for item in candidates_to_store:
        try:
            stored = await manager.remember(
                content=item["content"],
                user_id=payload.user_id,
                memory_type=item["memory_type"],
                source="conversation",
                task_context=f"session:{payload.session_id}" if payload.session_id else None,
                confidence=item["confidence"],
                risk_level=item["risk_level"],
                metadata={"auto_extracted": True, "prompt": payload.message},
            )
            extracted_records.append(stored)
        except Exception as e:
            logger.warning("Failed to store auto-extracted memory", error=str(e))

    # Also store the conversational turn in session memory if session_id provided
    if payload.session_id:
        try:
            session_rec = await manager.remember(
                content=f"User: {payload.message} | Assistant: {assistant_reply[:150]}",
                user_id=payload.user_id,
                memory_type=MemoryType.SESSION,
                source="chat_session",
                task_context=payload.session_id,
                confidence=0.7,
                metadata={"session_id": payload.session_id},
            )
            extracted_records.append(session_rec)
        except Exception as e:
            logger.debug("Session memory recording skipped", error=str(e))

    # Step 6: Return response + memory quality info
    return ChatResponse(
        response=assistant_reply,
        memories_used=selected_memories,
        search_results=search_results_data,
        memories_extracted=extracted_records,
    )


@router.post("/voice/transcribe")
async def transcribe_audio(
    payload: TranscribeRequest,
    stt: Optional[STTProvider] = Depends(get_stt),
) -> dict:
    """Transcribe base64 encoded audio using Deepgram STT."""
    if not stt or not stt.is_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Deepgram STT is not configured. Set DEEPGRAM_API_KEY.",
        )

    try:
        audio_bytes = base64.b64decode(payload.audio_base64)
        transcript = await stt.transcribe(audio_bytes, mime_type=payload.mime_type)
        return {"transcript": transcript}
    except Exception as e:
        logger.error("Audio transcription failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Transcription failed: {e}")


@router.post("/voice/speak")
async def speak_text(
    payload: SpeakRequest,
    tts: Optional[TTSProvider] = Depends(get_tts),
) -> Response:
    """Synthesize text into speech audio bytes using Deepgram TTS."""
    if not tts or not tts.is_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Deepgram TTS is not configured. Set DEEPGRAM_API_KEY.",
        )

    try:
        audio_bytes = await tts.synthesize(payload.text, voice=payload.voice)
        return Response(content=audio_bytes, media_type="audio/mpeg")
    except Exception as e:
        logger.error("Speech synthesis failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Speech synthesis failed: {e}")


@router.post("/search")
async def web_search(
    payload: SearchRequest,
    search: Optional[SearchProvider] = Depends(get_search),
) -> dict:
    """Query live web search via Tavily."""
    if not search or not search.is_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Tavily Search is not configured. Set TAVILY_API_KEY.",
        )

    try:
        results = await search.search(query=payload.query, max_results=payload.max_results)
        return {"query": payload.query, "results": [r.model_dump() for r in results]}
    except Exception as e:
        logger.error("Web search query failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Search failed: {e}")
