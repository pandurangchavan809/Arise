"""
FastAPI dependency injection providers.
Supplies singleton instances of storage backend, quality manager, LLM, search, and speech integrations.
"""

from __future__ import annotations

from typing import Optional

from adaptive_memory.config import Settings, get_settings
from adaptive_memory.core.manager import MemoryQualityManager
from adaptive_memory.integrations.llm.base import LLMProvider
from adaptive_memory.integrations.llm.nebius import NebiusProvider
from adaptive_memory.integrations.search.base import SearchProvider
from adaptive_memory.integrations.search.tavily import TavilyProvider
from adaptive_memory.integrations.speech.base import STTProvider, TTSProvider
from adaptive_memory.integrations.speech.deepgram import DeepgramSTT, DeepgramTTS
from adaptive_memory.storage.sqlite import SQLiteStorage

# Cached singletons
_storage: Optional[SQLiteStorage] = None
_manager: Optional[MemoryQualityManager] = None
_llm: Optional[LLMProvider] = None
_search: Optional[SearchProvider] = None
_stt: Optional[STTProvider] = None
_tts: Optional[TTSProvider] = None


def get_config() -> Settings:
    """Obtain application settings."""
    return get_settings()


async def get_storage() -> SQLiteStorage:
    """Obtain or initialize SQLite storage backend."""
    global _storage
    if _storage is None:
        settings = get_config()
        _storage = SQLiteStorage(database_url=settings.database_url)
        await _storage.initialize()
    return _storage


async def get_manager() -> MemoryQualityManager:
    """Obtain or initialize the Memory Quality Manager."""
    global _manager
    if _manager is None:
        storage = await get_storage()
        settings = get_config()
        _manager = MemoryQualityManager(storage=storage, config=settings)
    return _manager


def get_llm() -> Optional[LLMProvider]:
    """Obtain configured Nebius LLM provider."""
    global _llm
    if _llm is None:
        provider = NebiusProvider()
        _llm = provider
    return _llm


def get_search() -> Optional[SearchProvider]:
    """Obtain configured Tavily Search provider."""
    global _search
    if _search is None:
        provider = TavilyProvider()
        _search = provider
    return _search


def get_stt() -> Optional[STTProvider]:
    """Obtain Deepgram STT provider."""
    global _stt
    if _stt is None:
        provider = DeepgramSTT()
        _stt = provider
    return _stt


def get_tts() -> Optional[TTSProvider]:
    """Obtain Deepgram TTS provider."""
    global _tts
    if _tts is None:
        provider = DeepgramTTS()
        _tts = provider
    return _tts


async def cleanup_dependencies() -> None:
    """Gracefully close singleton connections during application lifespan shutdown."""
    global _storage, _manager, _llm, _search, _stt, _tts
    if _storage is not None:
        await _storage.close()
        _storage = None
    _manager = None
    _llm = None
    _search = None
    _stt = None
    _tts = None
