"""
Abstract Speech Provider interfaces for Adaptive Memory Runtime.
Provides STT (speech-to-text) and TTS (text-to-speech) contracts.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional


class STTProvider(ABC):
    """
    Abstract interface for Speech-to-Text transcription.
    """

    @abstractmethod
    def is_available(self) -> bool:
        """Check if STT provider is configured."""
        pass

    @abstractmethod
    async def transcribe(self, audio_data: bytes, mime_type: str = "audio/wav") -> str:
        """
        Transcribe raw audio bytes into text.
        """
        pass


class TTSProvider(ABC):
    """
    Abstract interface for Text-to-Speech synthesis.
    """

    @abstractmethod
    def is_available(self) -> bool:
        """Check if TTS provider is configured."""
        pass

    @abstractmethod
    async def synthesize(self, text: str, voice: Optional[str] = None) -> bytes:
        """
        Synthesize text into audio bytes.
        """
        pass
