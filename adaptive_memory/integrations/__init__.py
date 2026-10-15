"""
Integrations package for external services.
Subpackages:
- llm (Nebius Token Factory)
- search (Tavily)
- speech (Deepgram STT & TTS)
"""

from adaptive_memory.integrations.llm.base import LLMProvider
from adaptive_memory.integrations.llm.nebius import NebiusProvider
from adaptive_memory.integrations.search.base import SearchProvider, SearchResult
from adaptive_memory.integrations.search.tavily import TavilyProvider
from adaptive_memory.integrations.speech.base import STTProvider, TTSProvider
from adaptive_memory.integrations.speech.deepgram import DeepgramSTT, DeepgramTTS

__all__ = [
    "LLMProvider",
    "NebiusProvider",
    "SearchProvider",
    "SearchResult",
    "TavilyProvider",
    "STTProvider",
    "TTSProvider",
    "DeepgramSTT",
    "DeepgramTTS",
]
