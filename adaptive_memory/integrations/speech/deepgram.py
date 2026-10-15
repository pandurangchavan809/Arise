"""
Deepgram Speech integration provider.
Implements HTTP-based Speech-to-Text (STT) and Text-to-Speech (TTS).
"""

from __future__ import annotations

from typing import Optional
import httpx
import structlog

from adaptive_memory.config import get_settings
from adaptive_memory.integrations.speech.base import STTProvider, TTSProvider

logger = structlog.get_logger(__name__)


class DeepgramSTT(STTProvider):
    """
    Deepgram STT provider utilizing the HTTP audio transcription endpoint.
    """
    STT_ENDPOINT = "https://api.deepgram.com/v1/listen"

    def __init__(self, api_key: Optional[str] = None) -> None:
        settings = get_settings()
        self.api_key = api_key or settings.deepgram_api_key

    def is_available(self) -> bool:
        """Check if Deepgram credentials exist."""
        return bool(self.api_key)

    async def transcribe(self, audio_data: bytes, mime_type: str = "audio/wav") -> str:
        """Transcribe audio binary stream."""
        if not self.is_available():
            raise RuntimeError("Deepgram STT is not configured. Set DEEPGRAM_API_KEY.")

        headers = {
            "Authorization": f"Token {self.api_key}",
            "Content-Type": mime_type,
        }
        params = {
            "model": "nova-2",
            "smart_format": "true",
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.STT_ENDPOINT,
                    headers=headers,
                    params=params,
                    content=audio_data,
                )
                response.raise_for_status()
                data = response.json()

            channels = data.get("results", {}).get("channels", [])
            if channels:
                alternatives = channels[0].get("alternatives", [])
                if alternatives:
                    transcript = alternatives[0].get("transcript", "")
                    return transcript.strip()

            return ""
        except httpx.HTTPError as e:
            logger.error("Deepgram STT transcription failed", error=str(e))
            raise RuntimeError(f"Deepgram STT failed: {e}") from e
        except Exception as e:
            logger.error("Deepgram STT unexpected failure", error=str(e))
            raise


class DeepgramTTS(TTSProvider):
    """
    Deepgram TTS provider utilizing the HTTP text synthesis endpoint.
    """
    TTS_ENDPOINT = "https://api.deepgram.com/v1/speak"

    def __init__(self, api_key: Optional[str] = None) -> None:
        settings = get_settings()
        self.api_key = api_key or settings.deepgram_api_key
        self.default_voice = "aura-asteria-en"

    def is_available(self) -> bool:
        """Check if Deepgram credentials exist."""
        return bool(self.api_key)

    async def synthesize(self, text: str, voice: Optional[str] = None) -> bytes:
        """Synthesize text into speech audio bytes (MP3 container)."""
        if not self.is_available():
            raise RuntimeError("Deepgram TTS is not configured. Set DEEPGRAM_API_KEY.")

        target_voice = voice or self.default_voice
        headers = {
            "Authorization": f"Token {self.api_key}",
            "Content-Type": "application/json",
        }
        params = {
            "model": target_voice,
        }
        payload = {"text": text}

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.TTS_ENDPOINT,
                    headers=headers,
                    params=params,
                    json=payload,
                )
                response.raise_for_status()
                return response.content
        except httpx.HTTPError as e:
            logger.error("Deepgram TTS synthesis failed", voice=target_voice, error=str(e))
            raise RuntimeError(f"Deepgram TTS failed: {e}") from e
        except Exception as e:
            logger.error("Deepgram TTS unexpected failure", error=str(e))
            raise
