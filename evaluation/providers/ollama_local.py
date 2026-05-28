"""Local Ollama provider for testing on PC."""

import time
import requests
from .base import LLMProvider, LLMResponse


class OllamaLocalProvider(LLMProvider):
    """Ollama running locally on the development PC.

    This uses the same model and settings as deployed on Pi,
    allowing comparison of model behavior without Pi access.
    """

    def __init__(
        self,
        model: str = "qwen2.5:1.5b",
        url: str = "http://localhost:11434/api/generate",
        temperature: float = 0.1,
        num_predict: int = 80,
        num_ctx: int = 2048,
    ):
        self._model = model
        self._url = url
        self._options = {
            "temperature": temperature,
            "num_predict": num_predict,
            "num_ctx": num_ctx,
        }

    @property
    def name(self) -> str:
        return "ollama_local"

    @property
    def model_name(self) -> str:
        return self._model

    def generate(self, prompt: str) -> LLMResponse:
        start = time.perf_counter()
        try:
            response = requests.post(
                self._url,
                json={
                    "model": self._model,
                    "prompt": prompt,
                    "stream": False,
                    "options": self._options,
                    "keep_alive": "10m",
                },
                timeout=120,
            )
            response.raise_for_status()
            elapsed_ms = (time.perf_counter() - start) * 1000
            data = response.json()

            return LLMResponse(
                text=data.get("response", ""),
                inference_ms=elapsed_ms,
                model_name=self._model,
                provider=self.name,
                raw_response=data,
                tokens_used=data.get("eval_count"),
            )
        except requests.exceptions.ConnectionError as e:
            return LLMResponse(
                text="",
                inference_ms=(time.perf_counter() - start) * 1000,
                model_name=self._model,
                provider=self.name,
                error=f"Connection error: Ollama not running at {self._url}",
            )
        except requests.exceptions.Timeout:
            return LLMResponse(
                text="",
                inference_ms=(time.perf_counter() - start) * 1000,
                model_name=self._model,
                provider=self.name,
                error="Timeout: inference took too long",
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
            response = requests.get(
                self._url.replace("/api/generate", "/api/tags"),
                timeout=5,
            )
            if response.ok:
                models = response.json().get("models", [])
                return any(m.get("name", "").startswith(self._model.split(":")[0]) for m in models)
            return False
        except Exception:
            return False
