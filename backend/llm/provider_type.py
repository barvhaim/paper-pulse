"""Defines types for LLM providers used in the backend."""

from enum import Enum


class LLMProviderType(Enum):
    """Enum for LLM provider types."""

    OLLAMA = "ollama"
