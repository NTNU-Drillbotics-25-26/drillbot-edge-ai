"""Minimal evaluation server."""

import sys
import json
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import time

RESULTS_FILE = Path(__file__).parent / "results" / "evaluations.jsonl"

from app.hybrid import RetrievalMode
from app.retrieve import retrieve_chunks
from app.hybrid import retrieve_hybrid, format_context_block
from app.prompting import SYSTEM_PROMPT

from .providers import OllamaLocalProvider, OllamaRemoteProvider, OpenAIProvider
from .config import OPENAI_API_KEY, PI_HOST

app = FastAPI(title="Drillbot Evaluation")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Available models for testing
MODELS = [
    "qwen2.5:0.5b",
    "qwen2.5:1.5b",
    "qwen2.5:3b",
    "gemma2:2b",
    "phi3:mini",
    "llama3.2:1b",
    "llama3.2:3b",
]


def get_providers(model: str):
    """Create providers with specified model."""
    return {
        "local": OllamaLocalProvider(model=model),
        "pi": OllamaRemoteProvider(host=PI_HOST, model=model),
        "openai": OpenAIProvider(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None,
    }


class EvalRequest(BaseModel):
    question: str
    providers: list[str] = ["local"]
    mode: str = "fts"  # fts, embed, hybrid
    model: str = "qwen2.5:1.5b"  # model to use for local/pi


class SaveRequest(BaseModel):
    question: str
    mode: str
    model: str
    chunks: list[dict]
    retrieval_ms: int
    responses: dict
    scores: dict  # {local: 1-10, pi: 1-10, openai: 1-10}


def build_prompt(question: str, chunks: list, use_hybrid: bool = False) -> str:
    if not chunks:
        context = "No relevant documentation found."
    elif use_hybrid:
        context = format_context_block(chunks)
    else:
        parts = [f"## {c.title}\n{c.body}" for c in chunks]
        context = "\n\n".join(parts)
    return f"{SYSTEM_PROMPT}\n\n### Retrieved Documentation:\n{context}\n\n### Operator Question:\n{question}\n\n### Your Response:"


@app.get("/", response_class=HTMLResponse)
async def index():
    return FileResponse(Path(__file__).parent / "static" / "index.html")


@app.get("/status")
async def status():
    providers = get_providers("qwen2.5:1.5b")
    return {
        name: {"available": p.is_available(), "model": p.model_name} if p else {"available": False}
        for name, p in providers.items()
    }


@app.get("/models")
async def list_models():
    return MODELS


@app.post("/eval")
async def evaluate(req: EvalRequest):
    # Retrieve
    start = time.perf_counter()
    mode = RetrievalMode(req.mode)
    use_hybrid = mode in (RetrievalMode.HYBRID, RetrievalMode.EMBED)

    if mode == RetrievalMode.FTS:
        chunks = retrieve_chunks(req.question, None, limit=5)
        chunk_info = [{"title": c.title, "score": round(c.score, 2), "text": c.body} for c in chunks]
    else:
        chunks = retrieve_hybrid(req.question, None, mode=mode, final_limit=5)
        chunk_info = [{"title": c.title, "score": round(c.score, 2), "text": c.text} for c in chunks]

    retrieval_ms = (time.perf_counter() - start) * 1000
    prompt = build_prompt(req.question, chunks, use_hybrid=use_hybrid)

    # Generate from each provider
    providers = get_providers(req.model)
    results = {}
    for name in req.providers:
        p = providers.get(name)
        if not p or not p.is_available():
            results[name] = {"error": "not available"}
            continue
        resp = p.generate(prompt)
        results[name] = {
            "text": resp.text.strip(),
            "ms": round(resp.inference_ms),
            "model": p.model_name,
            "error": resp.error,
        }

    return {
        "question": req.question,
        "retrieval": {"ms": round(retrieval_ms), "chunks": chunk_info},
        "responses": results,
    }


@app.post("/save")
async def save_result(req: SaveRequest):
    RESULTS_FILE.parent.mkdir(exist_ok=True)
    record = {
        "timestamp": datetime.now().isoformat(),
        "question": req.question,
        "mode": req.mode,
        "model": req.model,
        "chunks": req.chunks,
        "retrieval_ms": req.retrieval_ms,
        "responses": req.responses,
        "scores": req.scores,
    }
    with open(RESULTS_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return {"saved": True}


@app.get("/results")
async def get_results():
    if not RESULTS_FILE.exists():
        return []
    results = []
    for line in RESULTS_FILE.read_text(encoding="utf-8").strip().split("\n"):
        if line:
            results.append(json.loads(line))
    return results


def main():
    import uvicorn
    print("Starting evaluation server at http://localhost:7861")
    uvicorn.run(app, host="0.0.0.0", port=7861)


if __name__ == "__main__":
    main()
