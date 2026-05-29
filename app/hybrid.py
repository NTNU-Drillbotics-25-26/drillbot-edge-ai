"""Hybrid retrieval combining FTS5 (curated FAQ) and embeddings (documents).

This module merges results from both retrieval systems, allowing the curated
FAQ to handle common operator questions while documents fill knowledge gaps.

Supports three retrieval strategies:
- FTS: Fast FAQ-only lookup (~10ms)
- HYBRID: Always queries both FTS and embeddings in parallel
- CASCADE: Smart routing - FTS first, adds embeddings only if FTS confidence is low
"""

from __future__ import annotations

import concurrent.futures
import logging
from dataclasses import dataclass
from enum import Enum

from .retrieve import retrieve_chunks, RetrievedChunk
from .retrieve_embed import retrieve_embedded, EmbeddingChunk

logger = logging.getLogger(__name__)

# Cascade mode thresholds
CASCADE_FTS_CONFIDENCE_THRESHOLD = 20.0  # If top FTS score >= this, skip embeddings (raised to check documents more often)
CASCADE_PARALLEL_TIMEOUT = 5.0  # Timeout for parallel queries in seconds


class RetrievalMode(str, Enum):
    """Available retrieval modes."""

    FTS = "fts"  # FTS5 only (curated FAQ)
    EMBED = "embed"  # Embeddings only (documents)
    HYBRID = "hybrid"  # Both combined (parallel)
    CASCADE = "cascade"  # Smart: FTS first, embeddings only if needed


@dataclass
class HybridChunk:
    """A chunk from either retrieval system with unified interface."""

    text: str
    title: str
    source: str
    source_type: str  # "faq" or "document"
    year: int | None
    score: float
    raw_score: float  # Original score before weighting
    # New fields for source attribution
    doc_type: str | None = None
    page_range: str | None = None


def _normalize_scores(scores: list[float]) -> list[float]:
    """Normalize scores to 0-1 range."""
    if not scores:
        return []
    max_score = max(scores)
    min_score = min(scores)
    if max_score == min_score:
        return [1.0] * len(scores)
    return [(s - min_score) / (max_score - min_score) for s in scores]


def _fts_to_hybrid_chunks(
    fts_chunks: list[RetrievedChunk],
    weight: float = 1.0,
) -> list[HybridChunk]:
    """Convert FTS chunks to HybridChunk format with normalized scoring."""
    if not fts_chunks:
        return []

    fts_scores = [c.score for c in fts_chunks]
    normalized = _normalize_scores(fts_scores)

    return [
        HybridChunk(
            text=chunk.body,
            title=chunk.title,
            source="curated",
            source_type="faq",
            year=None,
            score=norm_score * weight,
            raw_score=chunk.score,
        )
        for chunk, norm_score in zip(fts_chunks, normalized)
    ]


def _embed_to_hybrid_chunks(
    embed_chunks: list[EmbeddingChunk],
    weight: float = 1.0,
) -> list[HybridChunk]:
    """Convert embedding chunks to HybridChunk format with normalized scoring."""
    if not embed_chunks:
        return []

    embed_scores = [c.recency_score for c in embed_chunks]
    normalized = _normalize_scores(embed_scores)

    results = []
    for chunk, norm_score in zip(embed_chunks, normalized):
        # Build page range string if available
        page_range = None
        if chunk.page_start:
            if chunk.page_end and chunk.page_end != chunk.page_start:
                page_range = f"pp. {chunk.page_start}-{chunk.page_end}"
            else:
                page_range = f"p. {chunk.page_start}"

        results.append(
            HybridChunk(
                text=chunk.text,
                title=f"{chunk.source} ({chunk.year})",
                source=chunk.source,
                source_type="document",
                year=chunk.year,
                score=norm_score * weight,
                raw_score=chunk.recency_score,
                doc_type=chunk.doc_type,
                page_range=page_range,
            )
        )
    return results


def _deduplicate_chunks(
    chunks: list[HybridChunk],
    limit: int,
) -> list[HybridChunk]:
    """Deduplicate chunks by text prefix and return top results."""
    deduplicated = []
    seen_prefixes = set()

    for chunk in chunks:
        # Use first 100 chars as fingerprint
        prefix = chunk.text[:100].lower().strip()
        if prefix not in seen_prefixes:
            seen_prefixes.add(prefix)
            deduplicated.append(chunk)
        if len(deduplicated) >= limit:
            break

    return deduplicated


def retrieve_hybrid(
    question: str,
    fts_weight: float = 0.7,
    embed_weight: float = 0.3,
    fts_limit: int = 3,
    embed_limit: int = 3,
    final_limit: int = 3,
    mode: RetrievalMode = RetrievalMode.HYBRID,
) -> list[HybridChunk]:
    """
    Retrieve chunks using hybrid FTS5 + embedding approach.

    The curated FAQ (FTS5) is weighted higher by default because:
    - FAQ answers are verified and concise
    - Documents may have verbose, technical content

    Args:
        question: The user's question
        fts_weight: Weight for FTS5 results (0-1)
        embed_weight: Weight for embedding results (0-1)
        fts_limit: Max chunks from FTS5
        embed_limit: Max chunks from embeddings
        final_limit: Max total chunks to return
        mode: Retrieval mode (fts, embed, hybrid, or cascade)

    Returns:
        List of HybridChunk sorted by weighted score
    """
    # CASCADE mode uses special logic
    if mode == RetrievalMode.CASCADE:
        return retrieve_cascade(
            question,
            fts_weight=fts_weight,
            embed_weight=embed_weight,
            fts_limit=fts_limit,
            embed_limit=embed_limit,
            final_limit=final_limit,
        )

    results: list[HybridChunk] = []
    fts_chunks: list[RetrievedChunk] = []
    embed_chunks: list[EmbeddingChunk] = []

    # Determine what to fetch
    need_fts = mode in (RetrievalMode.FTS, RetrievalMode.HYBRID)
    need_embed = mode in (RetrievalMode.EMBED, RetrievalMode.HYBRID)

    # HYBRID mode: run both queries in parallel for speed
    if need_fts and need_embed:
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            fts_future = executor.submit(retrieve_chunks, question, fts_limit)
            embed_future = executor.submit(retrieve_embedded, question, embed_limit)

            try:
                fts_chunks = fts_future.result(timeout=CASCADE_PARALLEL_TIMEOUT)
                logger.info(f"FTS5 returned {len(fts_chunks)} chunks")
            except Exception as e:
                logger.error(f"FTS5 retrieval failed: {e}")
                fts_chunks = []

            try:
                embed_chunks = embed_future.result(timeout=CASCADE_PARALLEL_TIMEOUT)
                logger.info(f"Embeddings returned {len(embed_chunks)} chunks")
            except Exception as e:
                logger.error(f"Embedding retrieval failed: {e}")
                embed_chunks = []
    else:
        # Single source mode
        if need_fts:
            try:
                fts_chunks = retrieve_chunks(question, limit=fts_limit)
                logger.info(f"FTS5 returned {len(fts_chunks)} chunks")
            except Exception as e:
                logger.error(f"FTS5 retrieval failed: {e}")

        if need_embed:
            try:
                embed_chunks = retrieve_embedded(question, limit=embed_limit)
                logger.info(f"Embeddings returned {len(embed_chunks)} chunks")
            except Exception as e:
                logger.error(f"Embedding retrieval failed: {e}")

    # Convert to HybridChunk format
    results.extend(_fts_to_hybrid_chunks(fts_chunks, fts_weight))
    results.extend(_embed_to_hybrid_chunks(embed_chunks, embed_weight))

    # Sort by combined score
    results.sort(key=lambda r: r.score, reverse=True)

    return _deduplicate_chunks(results, final_limit)


def retrieve_cascade(
    question: str,
    fts_weight: float = 0.7,
    embed_weight: float = 0.3,
    fts_limit: int = 3,
    embed_limit: int = 3,
    final_limit: int = 3,
    confidence_threshold: float = CASCADE_FTS_CONFIDENCE_THRESHOLD,
) -> list[HybridChunk]:
    """
    Cascade hybrid retrieval: FTS first, embeddings only if needed.

    This is the recommended mode for operators - it's fast when FAQ has
    a confident answer, but automatically falls back to document search
    for complex or unfamiliar questions.

    Logic:
    1. Always run FTS (fast, ~10ms)
    2. If top FTS score >= threshold, use FTS only (high confidence)
    3. If FTS score is low, also query embeddings and merge results

    Args:
        question: The user's question
        fts_weight: Weight for FTS5 results when merging
        embed_weight: Weight for embedding results when merging
        fts_limit: Max chunks from FTS5
        embed_limit: Max chunks from embeddings
        final_limit: Max total chunks to return
        confidence_threshold: FTS score threshold for skipping embeddings

    Returns:
        List of HybridChunk sorted by score
    """
    # Step 1: Always run FTS (it's fast)
    try:
        fts_chunks = retrieve_chunks(question, limit=fts_limit)
        logger.info(f"CASCADE: FTS5 returned {len(fts_chunks)} chunks")
    except Exception as e:
        logger.error(f"CASCADE: FTS5 failed: {e}")
        fts_chunks = []

    # Step 2: Check confidence
    top_fts_score = fts_chunks[0].score if fts_chunks else 0

    if top_fts_score >= confidence_threshold:
        # High confidence - FAQ has a good match, skip embeddings
        logger.info(f"CASCADE: High FTS confidence ({top_fts_score:.1f} >= {confidence_threshold}), using FTS only")
        results = _fts_to_hybrid_chunks(fts_chunks, weight=1.0)
        return _deduplicate_chunks(results, final_limit)

    # Step 3: Low confidence - also query embeddings
    logger.info(f"CASCADE: Low FTS confidence ({top_fts_score:.1f} < {confidence_threshold}), adding embeddings")

    try:
        embed_chunks = retrieve_embedded(question, limit=embed_limit)
        logger.info(f"CASCADE: Embeddings returned {len(embed_chunks)} chunks")
    except Exception as e:
        logger.error(f"CASCADE: Embedding retrieval failed: {e}")
        embed_chunks = []

    # Merge results with weights
    results: list[HybridChunk] = []
    results.extend(_fts_to_hybrid_chunks(fts_chunks, fts_weight))
    results.extend(_embed_to_hybrid_chunks(embed_chunks, embed_weight))

    # Sort by combined score
    results.sort(key=lambda r: r.score, reverse=True)

    return _deduplicate_chunks(results, final_limit)


def retrieve_fts_only(
    question: str,
    limit: int = 3,
) -> list[HybridChunk]:
    """Retrieve using only FTS5 (curated FAQ)."""
    return retrieve_hybrid(
        question,
        fts_limit=limit,
        final_limit=limit,
        mode=RetrievalMode.FTS,
    )


def retrieve_embed_only(
    question: str,
    limit: int = 3,
) -> list[HybridChunk]:
    """Retrieve using only embeddings (documents)."""
    return retrieve_hybrid(
        question,
        embed_limit=limit,
        final_limit=limit,
        mode=RetrievalMode.EMBED,
    )


def format_context_block(chunks: list[HybridChunk]) -> str:
    """Format retrieved chunks into a context block for the LLM."""
    if not chunks:
        return "No relevant documentation found."

    parts = []
    for chunk in chunks:
        if chunk.year:
            header = f"## {chunk.title}"
        else:
            header = f"## {chunk.title}"
        parts.append(f"{header}\n{chunk.text}")

    return "\n\n".join(parts)
