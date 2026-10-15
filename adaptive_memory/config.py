"""
Configuration management for Adaptive Memory Runtime using Pydantic Settings.
Loads environment variables and supplies application-wide defaults.
"""

from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from adaptive_memory.models import EdgeBudget


class Settings(BaseSettings):
    """Runtime configuration settings."""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # Core & Database
    database_url: str = Field(default="sqlite:///./adaptive_memory.db", description="SQLite or DB connection string")
    log_level: str = Field(default="INFO", description="Logging verbosity")

    # Nebius Token Factory (LLM)
    nebius_api_key: Optional[str] = Field(default=None, description="Nebius API Key")
    nebius_base_url: str = Field(
        default="https://api.tokenfactory.nebius.com/v1",
        description="Nebius Token Factory base endpoint"
    )
    nebius_model: str = Field(
        default="meta-llama/Meta-Llama-3.1-70B-Instruct",
        description="Default Nebius LLM model"
    )

    # Tavily Web Search
    tavily_api_key: Optional[str] = Field(default=None, description="Tavily API key")

    # Deepgram Voice
    deepgram_api_key: Optional[str] = Field(default=None, description="Deepgram API key")

    # Edge Budget Defaults
    max_memories: int = Field(default=10, description="Default max memories to recall")
    max_context_tokens: int = Field(default=2000, description="Default token budget for memory block")
    max_latency_ms: int = Field(default=100, description="Target recall latency in ms")
    max_storage_bytes: int = Field(default=104857600, description="Local max storage bytes (default 100MB)")

    # Optional Embeddings
    embedding_enabled: bool = Field(default=False, description="Whether vector embedding is enabled")
    embedding_provider: Optional[str] = Field(default=None, description="Embedding provider (e.g., openai, nebius)")
    embedding_model: Optional[str] = Field(default=None, description="Embedding model name")

    def get_default_budget(self) -> EdgeBudget:
        """Construct an EdgeBudget instance from current settings."""
        return EdgeBudget(
            max_memories=self.max_memories,
            max_context_tokens=self.max_context_tokens,
            max_latency_ms=self.max_latency_ms,
            max_storage_bytes=self.max_storage_bytes,
        )


@lru_cache()
def get_settings() -> Settings:
    """Obtain cached Settings singleton."""
    return Settings()
