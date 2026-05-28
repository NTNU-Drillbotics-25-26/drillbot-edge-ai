"""Evaluation runner - executes questions across providers."""

from __future__ import annotations
import sys
import time
from pathlib import Path

# Add project root to path for app imports
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Deferred imports - only load app modules when needed
_app_loaded = False
_load_error = None


def _load_app_modules():
    """Load app modules on first use."""
    global _app_loaded, _load_error
    global retrieve_hybrid, format_context_block, RetrievalMode
    global retrieve_chunks, SYSTEM_PROMPT

    if _app_loaded:
        return True
    if _load_error:
        raise _load_error

    try:
        from app.hybrid import retrieve_hybrid, format_context_block, RetrievalMode
        from app.retrieve import retrieve_chunks
        from app.prompting import SYSTEM_PROMPT

        # Make them module-level
        globals()["retrieve_hybrid"] = retrieve_hybrid
        globals()["format_context_block"] = format_context_block
        globals()["RetrievalMode"] = RetrievalMode
        globals()["retrieve_chunks"] = retrieve_chunks
        globals()["SYSTEM_PROMPT"] = SYSTEM_PROMPT

        _app_loaded = True
        return True
    except ImportError as e:
        _load_error = ImportError(
            f"Failed to import app modules: {e}\n"
            f"Make sure all dependencies are installed:\n"
            f"  pip install chromadb sentence-transformers"
        )
        raise _load_error


from .providers.base import LLMProvider, LLMResponse
from .recorder import Recorder, EvaluationRecord


def build_prompt(question: str, chunks: list, use_hybrid: bool = False) -> str:
    """Build the prompt with retrieved context."""
    _load_app_modules()

    if use_hybrid:
        context_block = format_context_block(chunks)
    elif not chunks:
        context_block = "No relevant documentation found."
    else:
        context_parts = [f"## {c.title}\n{c.body}" for c in chunks]
        context_block = "\n\n".join(context_parts)

    return f"""{SYSTEM_PROMPT}

### Retrieved Documentation:
{context_block}

### Operator Question:
{question}

### Your Response:"""


def retrieve_context(
    question: str,
    mode=None,
    ui_context: dict | None = None,
    limit: int = 2,
) -> tuple[list, float, str, bool]:
    """
    Retrieve context chunks for a question.

    Returns: (chunks, retrieval_ms, mode_str, use_hybrid)
    """
    _load_app_modules()

    # Default to CASCADE mode for automatic FTS + embedding handling
    if mode is None:
        mode = RetrievalMode.CASCADE

    start = time.perf_counter()

    if mode == RetrievalMode.FTS:
        chunks = retrieve_chunks(question, limit=limit)
        use_hybrid = False
    else:
        # HYBRID, EMBED, and CASCADE all use retrieve_hybrid
        chunks = retrieve_hybrid(
            question,
            mode=mode,
            final_limit=limit,
        )
        use_hybrid = True

    retrieval_ms = (time.perf_counter() - start) * 1000
    return chunks, retrieval_ms, mode.value, use_hybrid


def chunks_to_dicts(chunks: list, use_hybrid: bool) -> list[dict]:
    """Convert chunks to serializable dicts."""
    result = []
    for c in chunks:
        if use_hybrid:
            result.append({
                "title": c.title,
                "source": c.source,
                "source_type": c.source_type,
                "score": c.score,
                "text": c.text,
            })
        else:
            result.append({
                "title": c.title,
                "score": c.score,
                "text": c.body,
            })
    return result


class EvaluationRunner:
    """Runs evaluations across multiple providers."""

    def __init__(
        self,
        providers: list[LLMProvider],
        retrieval_mode=None,
        output_dir: str = "evaluation/results",
        chunk_limit: int = 2,
    ):
        _load_app_modules()

        self.providers = providers
        # Default to CASCADE mode for smart FTS + embedding routing
        self.retrieval_mode = retrieval_mode or RetrievalMode.CASCADE
        self.chunk_limit = chunk_limit
        self.recorder = Recorder(output_dir)

    def run_question(
        self,
        question: str,
        verbose: bool = True,
    ) -> list[EvaluationRecord]:
        """Run a single question through all providers."""
        # Retrieve context (shared across all providers)
        chunks, retrieval_ms, mode_str, use_hybrid = retrieve_context(
            question,
            mode=self.retrieval_mode,
            limit=self.chunk_limit,
        )
        chunk_dicts = chunks_to_dicts(chunks, use_hybrid)
        prompt = build_prompt(question, chunks, use_hybrid=use_hybrid)

        if verbose:
            print(f"\n{'='*60}")
            print(f"Q: {question}")
            print(f"Retrieved {len(chunks)} chunks in {retrieval_ms:.1f}ms ({mode_str})")

        records = []
        for provider in self.providers:
            if verbose:
                print(f"\n--- {provider.name} ({provider.model_name}) ---")

            if not provider.is_available():
                if verbose:
                    print(f"  [SKIPPED] Provider not available")
                continue

            response = provider.generate(prompt)

            record = self.recorder.record(
                question=question,
                retrieval_mode=mode_str,
                retrieval_ms=retrieval_ms,
                chunks=chunk_dicts,
                provider=provider.name,
                model_name=provider.model_name,
                prompt=prompt,
                response=response.text,
                inference_ms=response.inference_ms,
                tokens_used=response.tokens_used,
                error=response.error,
            )
            records.append(record)

            if verbose:
                if response.error:
                    print(f"  ERROR: {response.error}")
                else:
                    print(f"  Response ({response.inference_ms:.0f}ms):")
                    print(f"  {response.text[:200]}...")

        return records

    def run_questions(
        self,
        questions: list[str],
        verbose: bool = True,
    ) -> list[EvaluationRecord]:
        """Run multiple questions through all providers."""
        all_records = []
        for i, question in enumerate(questions, 1):
            if verbose:
                print(f"\n[{i}/{len(questions)}]")
            records = self.run_question(question, verbose=verbose)
            all_records.extend(records)
        return all_records

    def save_results(self) -> tuple[Path, Path]:
        """Save all recorded results."""
        return self.recorder.save_all()

    def check_providers(self) -> dict[str, bool]:
        """Check availability of all providers."""
        return {p.name: p.is_available() for p in self.providers}
