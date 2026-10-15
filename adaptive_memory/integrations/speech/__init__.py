"""
Speech integration package.
Exposes STTProvider, TTSProvider, DeepgramSTT, and DeepgramTTS.
"""

from adaptive_memory.integrations.speech.base import STTProvider, TTSProvider
from adaptive_memory.integrations.speech.deepgram import DeepgramSTT, DeepgramTTS

__all__ = ["STTProvider", "TTSProvider", "DeepgramSTT", "DeepgramTTS"]
