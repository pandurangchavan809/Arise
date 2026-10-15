"""
Abstract LLM Provider interface for Adaptive Memory Runtime.
Defines contracts for chat completions, streaming responses, and optional embedding generation.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import AsyncIterator, Dict, List, Optional


class LLMProvider(ABC):
    """
    Abstract interface for LLM operations.
    """

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is configured and available for requests."""
        pass

    @abstractmethod
    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> str:
        """
        Generate completion for message sequence.
        """
        pass

    @abstractmethod
    async def chat_stream(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> AsyncIterator[str]:
        """
        Yield streaming text deltas for message sequence.
        """
        pass

    async def embed(self, texts: List[str]) -> List[List[float]]:
        """
        Optional vector embedding generation. Default raises NotImplementedError.
        """
        raise NotImplementedError("Embedding generation is not implemented by this provider.")
