"""
Nebius Token Factory LLM Provider implementation.
Uses an OpenAI-compatible client targeted at the Nebius Token Factory inference endpoint.
"""

from __future__ import annotations

from typing import AsyncIterator, Dict, List, Optional
from openai import AsyncOpenAI, OpenAIError
import structlog

from adaptive_memory.config import get_settings
from adaptive_memory.integrations.llm.base import LLMProvider

logger = structlog.get_logger(__name__)


class NebiusProvider(LLMProvider):
    """
    OpenAI-compatible client adapter for Nebius Token Factory.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        default_model: Optional[str] = None,
    ) -> None:
        settings = get_settings()
        self.api_key = api_key or settings.nebius_api_key
        self.base_url = base_url or settings.nebius_base_url
        self.default_model = default_model or settings.nebius_model

        self._client: Optional[AsyncOpenAI] = None
        if self.api_key:
            self._client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
            )

    def is_available(self) -> bool:
        """Verify API key configuration and readiness."""
        return bool(self.api_key and self._client is not None)

    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> str:
        """Generate complete chat response."""
        if not self.is_available():
            raise RuntimeError("Nebius LLM Provider is not configured. Set NEBIUS_API_KEY.")

        target_model = model or self.default_model
        try:
            assert self._client is not None
            response = await self._client.chat.completions.create(
                model=target_model,
                messages=messages,  # type: ignore
                temperature=temperature,
                max_tokens=max_tokens,
            )
            content = response.choices[0].message.content or ""
            return content.strip()
        except OpenAIError as e:
            logger.error("Nebius API chat completion failed", error=str(e), model=target_model)
            raise RuntimeError(f"Nebius chat completion failed: {e}") from e
        except Exception as e:
            logger.error("Unexpected error in Nebius chat completion", error=str(e))
            raise

    async def chat_stream(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> AsyncIterator[str]:
        """Stream chunks from Nebius Token Factory."""
        if not self.is_available():
            raise RuntimeError("Nebius LLM Provider is not configured. Set NEBIUS_API_KEY.")

        target_model = model or self.default_model
        try:
            assert self._client is not None
            stream = await self._client.chat.completions.create(
                model=target_model,
                messages=messages,  # type: ignore
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
            )
            async for chunk in stream:
                delta = chunk.choices[0].delta.content if chunk.choices else None
                if delta:
                    yield delta
        except OpenAIError as e:
            logger.error("Nebius streaming failed", error=str(e), model=target_model)
            raise RuntimeError(f"Nebius streaming failed: {e}") from e

    async def embed(self, texts: List[str]) -> List[List[float]]:
        """Optional embedding via OpenAI-compatible endpoint."""
        if not self.is_available():
            raise RuntimeError("Nebius LLM Provider is not configured.")

        settings = get_settings()
        emb_model = settings.embedding_model or "text-embedding-3-small"
        try:
            assert self._client is not None
            response = await self._client.embeddings.create(
                model=emb_model,
                input=texts,
            )
            return [data.embedding for data in response.data]
        except Exception as e:
            logger.error("Embedding generation failed", error=str(e))
            raise RuntimeError(f"Embedding failed: {e}") from e
