from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Iterable

from .db import DEFAULT_DB_PATH, get_connection


TOKEN_RE = re.compile(r"[A-Za-z0-9_]+")


@dataclass
class RetrievedChunk:
    doc_id: str
    title: str
    body: str
    status: str
    screen: str | None
    component: str | None
    aliases: list[str]
    raw_tags: list[str]
    source_type: str | None
    historic: bool
    score: float


def _tokenize(text: str) -> list[str]:
    return [token.lower() for token in TOKEN_RE.findall(text)]


def _make_fts_query(text: str) -> str:
    tokens = _tokenize(text)
    if not tokens:
        return ""
    # OR keeps retrieval forgiving for short operator questions and raw tag lookups.
    return " OR ".join(f'"{token}"' for token in tokens)


def _alias_bonus(question: str, aliases: Iterable[str], raw_tags: Iterable[str], title: str) -> float:
    haystack = question.lower()
    bonus = 0.0
    for alias in aliases:
        alias_l = alias.lower()
        if alias_l and alias_l in haystack:
            bonus += 8.0 if len(alias_l.split()) > 1 else 4.0
    for raw in raw_tags:
        raw_l = raw.lower()
        if raw_l and raw_l in haystack:
            bonus += 6.0
    if title.lower() in haystack:
        bonus += 5.0
    return bonus


def retrieve_chunks(
    question: str,
    limit: int = 5,
    db_path=DEFAULT_DB_PATH,
) -> list[RetrievedChunk]:
    conn = get_connection(db_path)

    fts_query = _make_fts_query(question)
    if not fts_query:
        return []

    rows = conn.execute(
        """
        SELECT
            c.id,
            c.doc_id,
            c.title,
            c.body,
            c.aliases,
            c.screen,
            c.component,
            c.raw_tags,
            c.status,
            c.source_type,
            c.historic,
            bm25(chunks_fts, 8.0, 3.0, 6.0, 2.0, 2.0, 4.0) AS rank
        FROM chunks_fts
        JOIN chunks c ON c.id = chunks_fts.rowid
        WHERE chunks_fts MATCH ?
        ORDER BY rank
        LIMIT ?
        """,
        (fts_query, limit * 3),
    ).fetchall()

    results = []
    for row in rows:
        aliases = json.loads(row["aliases"] or "[]")
        raw_tags = json.loads(row["raw_tags"] or "[]")
        base_score = -float(row["rank"])
        bonus = _alias_bonus(question, aliases, raw_tags, row["title"])
        total_score = base_score + bonus

        results.append(RetrievedChunk(
            doc_id=row["doc_id"],
            title=row["title"],
            body=row["body"],
            status=row["status"],
            screen=row["screen"],
            component=row["component"],
            aliases=aliases,
            raw_tags=raw_tags,
            source_type=row["source_type"],
            historic=bool(row["historic"]),
            score=total_score,
        ))

    conn.close()
    return sorted(results, key=lambda chunk: chunk.score, reverse=True)[:limit]
