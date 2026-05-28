"""FastAPI service for the Drillbot /ask endpoint."""

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import requests
import logging
import time
import hashlib
import json
import os
from typing import Generator

from .retrieve import retrieve_chunks
from .hybrid import retrieve_hybrid, format_context_block, RetrievalMode
from .prompting import SYSTEM_PROMPT
from .ingest import rebuild_database

# OpenAI configuration
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENAI_MODEL = "gpt-4o-mini"
OPENAI_MAX_TOKENS = 150

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Drillbot API")

OLLAMA_URL = "http://localhost:11434/api/generate"
# Balanced model for Pi 5 - fast enough, much less hallucination
# Pull with: ollama pull qwen2.5:1.5b
MODEL_NAME = "qwen2.5:1.5b"

# Ollama options - low temperature reduces hallucination
OLLAMA_OPTIONS = {
    "temperature": 0.1,  # Very low = more deterministic, less creative/hallucinatory
    "num_predict": 200,  # Max tokens in response
    "num_ctx": 2048,
    "num_thread": 4,     # Pi 5 has 4 cores
}

# Cache settings
CACHE_ENABLED = True
CACHE_MAX_SIZE = 64

# Retrieval settings
# Options: "fts" (FAQ only), "embed" (documents only), "hybrid" (both), "cascade" (smart)
# CASCADE is recommended: FTS first (~10ms), adds embeddings only if FTS confidence is low
# This gives operators seamless access to both FAQ and design documents.
RETRIEVAL_MODE = RetrievalMode.CASCADE  # Smart routing - fast for FAQ, falls back to docs
FTS_WEIGHT = 0.75  # Weight for curated FAQ results (higher = trust FAQ more)
EMBED_WEIGHT = 0.25  # Weight for document results
FINAL_CHUNK_LIMIT = 2  # Chunks to provide to LLM (more context for small models)


class AskRequest(BaseModel):
    question: str
    stream: bool = False  # Enable streaming responses
    use_documents: bool = False  # DEPRECATED: Cascade mode now handles this automatically
    force_mode: str | None = None  # Override retrieval mode: "fts", "embed", "hybrid", "cascade"
    provider: str = "ollama"  # "ollama" (Pi) or "openai" (cloud)


class TimingInfo(BaseModel):
    retrieval_ms: float
    llm_ms: float
    total_ms: float
    cached: bool = False


class SourceInfo(BaseModel):
    """Detailed source attribution for a chunk."""
    filename: str
    year: int | None
    doc_type: str | None = None
    page_range: str | None = None


class AskResponse(BaseModel):
    answer: str
    sources: list[str]  # Backward compatible
    source_details: list[SourceInfo] | None = None  # NEW: detailed source info
    chunks_used: int
    timing: TimingInfo | None = None
    provider_used: str | None = None  # "ollama" or "openai"
    retrieval_mode: str | None = None  # "fts", "embed", "hybrid", or "cascade"


class RetrievalDebugResponse(BaseModel):
    """Debug info showing what was retrieved."""
    question: str
    mode: str  # "fts" or "hybrid"
    chunks_retrieved: int
    chunks: list[dict]  # Full chunk details


def call_ollama(prompt: str) -> tuple[str, float]:
    """Call Ollama and return (response, inference_time_ms)."""
    start = time.perf_counter()
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False,
                "options": OLLAMA_OPTIONS,
                "keep_alive": "10m",  # Keep model loaded for 10 minutes
            },
            timeout=120
        )
        response.raise_for_status()
        elapsed_ms = (time.perf_counter() - start) * 1000
        return response.json().get("response", "No response generated."), elapsed_ms
    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=503, detail="Ollama service not running")
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="Model inference timeout")
    except Exception as e:
        logger.error(f"Ollama error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def stream_ollama(prompt: str) -> Generator[str, None, None]:
    """Stream response from Ollama token by token."""
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": True,
                "options": OLLAMA_OPTIONS,
                "keep_alive": "10m",
            },
            timeout=120,
            stream=True
        )
        response.raise_for_status()
        for line in response.iter_lines():
            if line:
                data = json.loads(line)
                if "response" in data:
                    yield data["response"]
    except Exception as e:
        logger.error(f"Ollama stream error: {e}")
        yield f"Error: {e}"


def call_openai(prompt: str) -> tuple[str, float]:
    """Call OpenAI API and return (response, inference_time_ms)."""
    start = time.perf_counter()
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=OPENAI_MAX_TOKENS,
        )
        elapsed_ms = (time.perf_counter() - start) * 1000
        return response.choices[0].message.content or "", elapsed_ms
    except ImportError:
        raise HTTPException(status_code=500, detail="openai package not installed")
    except Exception as e:
        logger.error(f"OpenAI error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def call_llm(prompt: str, provider: str) -> tuple[str, float, str]:
    """Call LLM based on provider. Returns (response, inference_ms, provider_used)."""
    if provider == "openai":
        if not OPENAI_API_KEY:
            raise HTTPException(status_code=500, detail="OPENAI_API_KEY not configured")
        answer, ms = call_openai(prompt)
        return answer, ms, "openai"
    else:
        answer, ms = call_ollama(prompt)
        return answer, ms, "ollama"


def _cache_key(question: str, provider: str) -> str:
    """Generate cache key from question and provider."""
    return hashlib.md5(f"{question.lower().strip()}|{provider}".encode()).hexdigest()


# Simple response cache
_response_cache: dict[str, AskResponse] = {}


def get_cached_response(key: str) -> AskResponse | None:
    """Get cached response if available."""
    if not CACHE_ENABLED:
        return None
    return _response_cache.get(key)


def cache_response(key: str, response: AskResponse) -> None:
    """Cache a response, evicting oldest if at capacity."""
    if not CACHE_ENABLED:
        return
    if len(_response_cache) >= CACHE_MAX_SIZE:
        # Remove oldest entry (first inserted)
        oldest = next(iter(_response_cache))
        del _response_cache[oldest]
    _response_cache[key] = response


def build_prompt(question: str, chunks: list, use_hybrid: bool = False) -> str:
    if use_hybrid:
        # HybridChunk uses .text instead of .body
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


@app.on_event("startup")
def startup_event():
    logger.info("Initializing Drillbot database...")
    try:
        count = rebuild_database()
        logger.info(f"Indexed {count} documentation chunks")
    except Exception as e:
        logger.error(f"Database init failed: {e}")


@app.get("/health")
def health_check():
    """Health check with model and cache info."""
    return {
        "status": "ok",
        "model": MODEL_NAME,
        "retrieval_mode": RETRIEVAL_MODE.value,
        "fts_weight": FTS_WEIGHT,
        "embed_weight": EMBED_WEIGHT,
        "chunk_limit": FINAL_CHUNK_LIMIT,
        "cache_enabled": CACHE_ENABLED,
        "cache_size": len(_response_cache),
        "cache_max": CACHE_MAX_SIZE,
        "ollama_options": OLLAMA_OPTIONS,
        "openai_configured": bool(OPENAI_API_KEY),
    }


@app.get("/providers")
def list_providers():
    """List available LLM providers and their status."""
    providers = []

    # Check Ollama availability
    ollama_available = False
    try:
        resp = requests.get("http://localhost:11434/api/tags", timeout=2)
        ollama_available = resp.status_code == 200
    except Exception:
        pass

    providers.append({
        "id": "ollama",
        "name": "Ollama (Pi)",
        "model": MODEL_NAME,
        "available": ollama_available,
    })

    # Check OpenAI availability
    openai_available = bool(OPENAI_API_KEY)
    providers.append({
        "id": "openai",
        "name": "OpenAI (Cloud)",
        "model": OPENAI_MODEL,
        "available": openai_available,
    })

    return {"providers": providers}


@app.post("/cache/clear")
def clear_cache():
    """Clear the response cache."""
    count = len(_response_cache)
    _response_cache.clear()
    logger.info(f"Cleared {count} cached responses")
    return {"cleared": count}


@app.post("/warmup")
def warmup_model():
    """Pre-load the model to avoid cold start latency."""
    start = time.perf_counter()
    try:
        requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": "Hello",
                "stream": False,
                "options": {"num_predict": 1},
                "keep_alive": "10m",
            },
            timeout=60
        )
        elapsed = (time.perf_counter() - start) * 1000
        return {"status": "warm", "model": MODEL_NAME, "warmup_ms": round(elapsed, 2)}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Warmup failed: {e}")


@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    total_start = time.perf_counter()
    logger.info(f"Question: {req.question} (provider={req.provider})")

    # Check cache first
    cache_key = _cache_key(req.question, req.provider)
    cached = get_cached_response(cache_key)
    if cached:
        logger.info("Cache hit")
        # Update timing to show it was cached
        if cached.timing:
            cached.timing.cached = True
        return cached

    # Retrieval phase - cascade mode handles FTS vs embedding automatically
    retrieval_start = time.perf_counter()

    # Determine effective mode: force_mode > use_documents (legacy) > default
    if req.force_mode:
        try:
            effective_mode = RetrievalMode(req.force_mode)
        except ValueError:
            effective_mode = RETRIEVAL_MODE
    elif req.use_documents:
        # Legacy support: use_documents=true forces HYBRID mode
        effective_mode = RetrievalMode.HYBRID
    else:
        effective_mode = RETRIEVAL_MODE

    # All modes except pure FTS use hybrid chunk format
    use_hybrid = effective_mode in (RetrievalMode.HYBRID, RetrievalMode.EMBED, RetrievalMode.CASCADE)

    if effective_mode == RetrievalMode.FTS:
        chunks = retrieve_chunks(req.question, limit=FINAL_CHUNK_LIMIT)
    else:
        chunks = retrieve_hybrid(
            req.question,
            fts_weight=FTS_WEIGHT,
            embed_weight=EMBED_WEIGHT,
            mode=effective_mode,
            final_limit=FINAL_CHUNK_LIMIT,
        )

    retrieval_ms = (time.perf_counter() - retrieval_start) * 1000
    logger.info(f"Retrieved {len(chunks)} chunks in {retrieval_ms:.1f}ms (mode={effective_mode.value})")

    prompt = build_prompt(req.question, chunks, use_hybrid=use_hybrid)

    # Streaming response (only supported for Ollama currently)
    if req.stream:
        if req.provider == "openai":
            raise HTTPException(status_code=400, detail="Streaming not supported for OpenAI provider")
        def generate():
            for token in stream_ollama(prompt):
                yield token
        return StreamingResponse(generate(), media_type="text/plain")

    # Standard response with LLM timing
    answer, llm_ms, provider_used = call_llm(prompt, req.provider)
    total_ms = (time.perf_counter() - total_start) * 1000

    logger.info(f"LLM ({provider_used}) took {llm_ms:.0f}ms, total {total_ms:.0f}ms")

    # Extract source titles based on chunk type
    if use_hybrid:
        sources = [c.title for c in chunks]
        source_details = [
            SourceInfo(
                filename=c.source,
                year=c.year,
                doc_type=c.doc_type,
                page_range=c.page_range,
            )
            for c in chunks
        ]
    else:
        sources = [c.title for c in chunks]
        source_details = None  # FTS chunks don't have detailed source info

    response = AskResponse(
        answer=answer.strip(),
        sources=sources,
        source_details=source_details,
        chunks_used=len(chunks),
        timing=TimingInfo(
            retrieval_ms=round(retrieval_ms, 2),
            llm_ms=round(llm_ms, 2),
            total_ms=round(total_ms, 2),
            cached=False
        ),
        provider_used=provider_used,
        retrieval_mode=effective_mode.value,
    )

    # Cache the response
    cache_response(cache_key, response)

    return response


@app.post("/ask/stream")
def ask_stream(req: AskRequest):
    """Dedicated streaming endpoint for better UX. Only supports Ollama provider."""
    if req.provider == "openai":
        raise HTTPException(status_code=400, detail="Streaming not supported for OpenAI provider")

    logger.info(f"Streaming question: {req.question}")

    # Determine effective mode (same logic as /ask)
    if req.force_mode:
        try:
            effective_mode = RetrievalMode(req.force_mode)
        except ValueError:
            effective_mode = RETRIEVAL_MODE
    elif req.use_documents:
        effective_mode = RetrievalMode.HYBRID
    else:
        effective_mode = RETRIEVAL_MODE

    use_hybrid = effective_mode in (RetrievalMode.HYBRID, RetrievalMode.EMBED, RetrievalMode.CASCADE)

    if effective_mode == RetrievalMode.FTS:
        chunks = retrieve_chunks(req.question, limit=FINAL_CHUNK_LIMIT)
    else:
        chunks = retrieve_hybrid(
            req.question,
            fts_weight=FTS_WEIGHT,
            embed_weight=EMBED_WEIGHT,
            mode=effective_mode,
            final_limit=FINAL_CHUNK_LIMIT,
        )

    prompt = build_prompt(req.question, chunks, use_hybrid=use_hybrid)

    def generate():
        for token in stream_ollama(prompt):
            yield token

    return StreamingResponse(generate(), media_type="text/plain")


@app.get("/documents/stats")
def document_stats():
    """Get statistics about indexed design documents."""
    try:
        from .ingest_docs import get_document_stats
        return get_document_stats()
    except Exception as e:
        logger.error(f"Document stats error: {e}")
        return {"error": str(e), "total_chunks": 0}


@app.post("/documents/ingest")
def ingest_documents():
    """Re-ingest all design documents from the documents/ directory."""
    try:
        from .ingest_docs import ingest_documents as do_ingest
        count = do_ingest()
        # Clear cache since documents changed
        _response_cache.clear()
        logger.info(f"Ingested {count} document chunks, cache cleared")
        return {"status": "ok", "chunks_indexed": count}
    except Exception as e:
        logger.error(f"Document ingest error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ask/debug", response_model=RetrievalDebugResponse)
def ask_debug(req: AskRequest):
    """
    Debug endpoint: shows retrieved chunks without calling LLM.
    Useful for inspecting retrieval quality and scores.
    """
    # Determine effective mode (same logic as /ask)
    if req.force_mode:
        try:
            effective_mode = RetrievalMode(req.force_mode)
        except ValueError:
            effective_mode = RETRIEVAL_MODE
    elif req.use_documents:
        effective_mode = RetrievalMode.HYBRID
    else:
        effective_mode = RETRIEVAL_MODE

    # For debug, show more chunks (5) to see ranking quality
    debug_limit = 5

    if effective_mode == RetrievalMode.FTS:
        chunks = retrieve_chunks(req.question, limit=debug_limit)
        chunk_info = [
            {
                "rank": i + 1,
                "title": c.title,
                "score": round(c.score, 3),
                "source_type": "faq",
                "preview": c.body[:300] + "..." if len(c.body) > 300 else c.body,
            }
            for i, c in enumerate(chunks)
        ]
    elif effective_mode in (RetrievalMode.HYBRID, RetrievalMode.CASCADE):
        # Show hybrid/cascade results with full context
        chunks = retrieve_hybrid(
            req.question,
            fts_weight=FTS_WEIGHT,
            embed_weight=EMBED_WEIGHT,
            mode=effective_mode,
            final_limit=debug_limit,
        )
        chunk_info = [
            {
                "rank": i + 1,
                "title": c.title,
                "source": c.source,
                "source_type": c.source_type,
                "year": c.year,
                "doc_type": c.doc_type,
                "page_range": c.page_range,
                "score": round(c.score, 3),
                "raw_score": round(c.raw_score, 3),
                "preview": c.text[:300] + "..." if len(c.text) > 300 else c.text,
            }
            for i, c in enumerate(chunks)
        ]
    else:
        # EMBED only mode
        from .retrieve_embed import retrieve_embedded
        chunks = retrieve_embedded(req.question, limit=debug_limit)
        chunk_info = [
            {
                "rank": i + 1,
                "source": c.source,
                "year": c.year,
                "doc_type": c.doc_type,
                "page_range": f"pp. {c.page_start}-{c.page_end}" if c.page_start else None,
                "similarity": round(c.similarity, 3),
                "recency_score": round(c.recency_score, 3),
                "source_type": "document",
                "preview": c.text[:300] + "..." if len(c.text) > 300 else c.text,
            }
            for i, c in enumerate(chunks)
        ]

    return RetrievalDebugResponse(
        question=req.question,
        mode=effective_mode.value,
        chunks_retrieved=len(chunk_info),
        chunks=chunk_info,
    )
