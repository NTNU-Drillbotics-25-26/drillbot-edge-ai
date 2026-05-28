"""Remote Ollama provider for connecting to Pi over network."""

import time
import requests
from .base import LLMProvider, LLMResponse


class OllamaRemoteProvider(LLMProvider):
    """Ollama running on the Raspberry Pi.

    Connects over the network to test actual Pi performance.
    """

    def __init__(
        self,
        host: str = "10.22.60.223",
        port: int = 11434,
        model: str = "qwen2.5:1.5b",
        temperature: float = 0.1,
        num_predict: int = 80,
        num_ctx: int = 2048,
    ):
        self._host = host
        self._port = port
        self._model = model
        self._url = f"http://{host}:{port}/api/generate"
        self._options = {
            "temperature": temperature,
            "num_predict": num_predict,
            "num_ctx": num_ctx,
            "num_thread": 4,  # Pi 5 has 4 cores
        }

    @property
    def name(self) -> str:
        return "ollama_remote"

    @property
    def model_name(self) -> str:
        return f"{self._model}@{self._host}"

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
                timeout=180,  # Longer timeout for Pi
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
        except requests.exceptions.ConnectionError:
            return LLMResponse(
                text="",
                inference_ms=(time.perf_counter() - start) * 1000,
                model_name=self._model,
                provider=self.name,
                error=f"Connection error: Cannot reach Pi at {self._host}:{self._port}",
            )
        except requests.exceptions.Timeout:
            return LLMResponse(
                text="",
                inference_ms=(time.perf_counter() - start) * 1000,
                model_name=self._model,
                provider=self.name,
                error="Timeout: Pi inference took too long",
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
                f"http://{self._host}:{self._port}/api/tags",
                timeout=10,
            )
            if response.ok:
                models = response.json().get("models", [])
                return any(m.get("name", "").startswith(self._model.split(":")[0]) for m in models)
            return False
        except Exception:
            return False
