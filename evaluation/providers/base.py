"""Abstract base class for LLM providers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class LLMResponse:
    """Standardized response from any LLM provider."""

    text: str
    inference_ms: float
    model_name: str
    provider: str
    raw_response: dict[str, Any] = field(default_factory=dict)
    tokens_used: int | None = None
    error: str | None = None

    @property
    def success(self) -> bool:
        return self.error is None


class LLMProvider(ABC):
    """Abstract interface for LLM providers."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider identifier (e.g., 'ollama_local', 'openai')."""
        ...

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Model being used (e.g., 'qwen2.5:1.5b', 'gpt-4o-mini')."""
        ...

    @abstractmethod
    def generate(self, prompt: str) -> LLMResponse:
        """Generate a response for the given prompt."""
        ...

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this provider is currently available."""
        ...

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(model={self.model_name})"
