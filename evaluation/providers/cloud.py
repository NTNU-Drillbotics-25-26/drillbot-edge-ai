"""Cloud LLM providers (OpenAI)."""

import time
from .base import LLMProvider, LLMResponse


class OpenAIProvider(LLMProvider):
    """OpenAI GPT models for A/B comparison."""

    def __init__(
        self,
        model: str = "gpt-4o-mini",
        api_key: str | None = None,
        temperature: float = 0.1,
        max_tokens: int = 150,
    ):
        self._model = model
        self._temperature = temperature
        self._max_tokens = max_tokens
        self._api_key = api_key
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                from openai import OpenAI
            except ImportError:
                raise ImportError("openai package required: pip install openai")

            if self._api_key:
                self._client = OpenAI(api_key=self._api_key)
            else:
                # Will use OPENAI_API_KEY env var
                self._client = OpenAI()
        return self._client

    @property
    def name(self) -> str:
        return "openai"

    @property
    def model_name(self) -> str:
        return self._model

    def generate(self, prompt: str) -> LLMResponse:
        start = time.perf_counter()
        try:
            client = self._get_client()
            response = client.chat.completions.create(
                model=self._model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self._temperature,
                max_tokens=self._max_tokens,
            )
            elapsed_ms = (time.perf_counter() - start) * 1000

            message = response.choices[0].message.content or ""
            tokens = response.usage.total_tokens if response.usage else None

            return LLMResponse(
                text=message,
                inference_ms=elapsed_ms,
                model_name=self._model,
                provider=self.name,
                raw_response=response.model_dump(),
                tokens_used=tokens,
            )
        except ImportError as e:
            return LLMResponse(
                text="",
                inference_ms=(time.perf_counter() - start) * 1000,
                model_name=self._model,
                provider=self.name,
                error=str(e),
            )
        except Exception as e:
            return LLMResponse(
                text="",
                inference_ms=(time.perf_counter() - start) * 1000,
                model_name=self._model,
                provider=self.name,
                error=str(e),
            )

    def is_available(self) -> bool:
        try:
            client = self._get_client()
            # Quick model list check
            client.models.retrieve(self._model)
            return True
        except Exception:
            return False
