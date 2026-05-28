"""Embedding-based retrieval for design documents.

Uses ChromaDB vector store with Ollama embeddings for semantic search.
Includes recency boosting to prefer newer documents.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime

from .ingest_docs import get_collection

logger = logging.getLogger(__name__)

# Current year for recency calculations
CURRENT_YEAR = datetime.now().year


@dataclass
class EmbeddingChunk:
    """A chunk retrieved via embedding similarity."""

    text: str
    source: str
    source_path: str
    year: int
    chunk_index: int
    similarity: float
    recency_score: float  # Similarity adjusted for document age
    # Fields for source attribution
    doc_type: str | None = None
    page_start: int | None = None
    page_end: int | None = None
    # Structural metadata (from hierarchical chunking)
    heading_path: str | None = None
    structural_level: int | None = None
    section_title: str | None = None

    @property
    def citation(self) -> str:
        """Return formatted citation string with structural context."""
        parts = [f"{self.source} ({self.year})"]

        # Add page range if available
        if self.page_start:
            if self.page_end and self.page_end != self.page_start:
                parts.append(f"pp. {self.page_start}-{self.page_end}")
            else:
                parts.append(f"p. {self.page_start}")

        # Add section context if available (from structural chunking)
        if self.heading_path and self.heading_path != "Document":
            parts.append(f"§ {self.heading_path}")

        return " | ".join(parts)


def retrieve_embedded(
    question: str,
    limit: int = 5,
    year_boost: float = 0.05,
    min_year: int | None = None,
    max_year: int | None = None,
) -> list[EmbeddingChunk]:
    """
    Retrieve document chunks using embedding similarity.

    Args:
        question: The user's question
        limit: Maximum number of chunks to return
        year_boost: Score boost per year closer to current (0.05 = 5% per year)
        min_year: Only include documents from this year or later
        max_year: Only include documents from this year or earlier

    Returns:
        List of EmbeddingChunk sorted by recency-adjusted score
    """
    try:
        collection = get_collection()
    except Exception as e:
        logger.error(f"Failed to get collection: {e}")
        return []

    # Build where clause for year filtering
    where = None
    if min_year is not None and max_year is not None:
        where = {"$and": [{"year": {"$gte": min_year}}, {"year": {"$lte": max_year}}]}
    elif min_year is not None:
        where = {"year": {"$gte": min_year}}
    elif max_year is not None:
        where = {"year": {"$lte": max_year}}

    try:
        # Fetch more than needed for reranking
        n_results = min(limit * 3, 20)

        query_params = {
            "query_texts": [question],
            "n_results": n_results,
            "include": ["documents", "metadatas", "distances"],
        }
        if where:
            query_params["where"] = where

        results = collection.query(**query_params)
    except Exception as e:
        logger.error(f"Query failed: {e}")
        return []

    if not results["ids"] or not results["ids"][0]:
        return []

    chunks = []
    for doc, meta, distance in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        # ChromaDB cosine distance: 0 = identical, 2 = opposite
        # Convert to similarity: 1 = identical, 0 = orthogonal, -1 = opposite
        similarity = 1 - distance

        # Recency boost: newer documents score higher
        year = meta.get("year", CURRENT_YEAR)
        years_old = CURRENT_YEAR - year
        # Boost ranges from 0 (5+ years old) to year_boost * 5 (current year)
        recency_bonus = max(0, (5 - years_old)) * year_boost

        chunks.append(
            EmbeddingChunk(
                text=doc,
                source=meta.get("source", "unknown"),
                source_path=meta.get("source_path", ""),
                year=year,
                chunk_index=meta.get("chunk_index", 0),
                similarity=similarity,
                recency_score=similarity + recency_bonus,
                doc_type=meta.get("doc_type"),
                page_start=meta.get("page_start"),
                page_end=meta.get("page_end"),
                # Structural metadata
                heading_path=meta.get("heading_path"),
                structural_level=meta.get("structural_level"),
                section_title=meta.get("section_title"),
            )
        )

    # Sort by recency-adjusted score (highest first)
    chunks.sort(key=lambda c: c.recency_score, reverse=True)

    return chunks[:limit]


def retrieve_by_year(
    question: str,
    year: int,
    limit: int = 5,
) -> list[EmbeddingChunk]:
    """
    Retrieve chunks from a specific year only.

    Useful for questions like "What did the 2024 design say about X?"
    """
    return retrieve_embedded(question, limit=limit, min_year=year, max_year=year)


def retrieve_recent(
    question: str,
    years_back: int = 2,
    limit: int = 5,
) -> list[EmbeddingChunk]:
    """
    Retrieve chunks from recent years only.

    Args:
        question: The user's question
        years_back: How many years back to search (default 2)
        limit: Maximum chunks to return
    """
    min_year = CURRENT_YEAR - years_back
    return retrieve_embedded(question, limit=limit, min_year=min_year)
