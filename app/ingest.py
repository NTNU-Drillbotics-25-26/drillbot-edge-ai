from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from app.db import (
        DEFAULT_DB_PATH,
        FALLBACK_DB_PATH,
        get_connection,
        get_default_db_path,
        init_db,
        make_temp_db_path,
    )
else:
    from .db import (
        DEFAULT_DB_PATH,
        FALLBACK_DB_PATH,
        get_connection,
        get_default_db_path,
        init_db,
        make_temp_db_path,
    )


DOCS_DIR = Path(__file__).resolve().parents[1] / "docs"


@dataclass
class ChunkDoc:
    """Structured representation of one markdown manual chunk."""
    doc_id: str
    title: str
    aliases: list[str]
    screen: str | None
    component: str | None
    raw_tags: list[str]
    status: str
    source_type: str | None
    historic: bool
    body: str


def _parse_front_matter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---\n"):
        raise ValueError("Markdown file is missing front matter.")

    try:
        _, raw_meta, body = text.split("---\n", 2)
    except ValueError as exc:
        raise ValueError("Invalid front matter block.") from exc

    meta: dict[str, Any] = {}
    current_key: str | None = None

    for raw_line in raw_meta.splitlines():
        if not raw_line.strip():
            continue
        # The seed docs use a small YAML-like subset, so a lightweight parser is enough here.
        if raw_line.startswith("  - "):
            if current_key is None:
                raise ValueError(f"List item without key: {raw_line}")
            meta.setdefault(current_key, []).append(raw_line[4:].strip())
            continue

        key, _, value = raw_line.partition(":")
        key = key.strip()
        value = value.strip()
        current_key = key

        if not value:
            meta[key] = []
        elif value.lower() in {"true", "false"}:
            meta[key] = value.lower() == "true"
        else:
            meta[key] = value

    return meta, body.strip()


def parse_markdown(path: Path) -> ChunkDoc:
    meta, body = _parse_front_matter(path.read_text(encoding="utf-8"))
    required = ["id", "title", "status"]
    missing = [key for key in required if key not in meta or not meta[key]]
    if missing:
        raise ValueError(f"{path} is missing required metadata: {', '.join(missing)}")

    return ChunkDoc(
        doc_id=str(meta["id"]),
        title=str(meta["title"]),
        aliases=list(meta.get("aliases", [])),
        screen=meta.get("screen"),
        component=meta.get("component"),
        raw_tags=list(meta.get("raw_tags", [])),
        status=str(meta["status"]),
        source_type=meta.get("source_type"),
        historic=bool(meta.get("historic", False)),
        body=body,
    )


def iter_markdown_files(docs_dir: Path = DOCS_DIR) -> list[Path]:
    return sorted(docs_dir.rglob("*.md"))


def rebuild_database(db_path: Path | None = None, docs_dir: Path = DOCS_DIR) -> int:
    conn = get_connection(db_path or DEFAULT_DB_PATH)
    init_db(conn)

    # Rebuild from scratch so the FTS index always matches the markdown source of truth.
    conn.execute("DELETE FROM chunks_fts")
    conn.execute("DELETE FROM chunks")

    count = 0
    for path in iter_markdown_files(docs_dir):
        doc = parse_markdown(path)
        cursor = conn.execute(
            """
            INSERT INTO chunks (
                doc_id, title, body, aliases, screen, component, raw_tags, status, source_type, historic
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                doc.doc_id,
                doc.title,
                doc.body,
                json.dumps(doc.aliases),
                doc.screen,
                doc.component,
                json.dumps(doc.raw_tags),
                doc.status,
                doc.source_type,
                1 if doc.historic else 0,
            ),
        )
        row_id = cursor.lastrowid
        # Insert searchable text separately because FTS5 is backed by the main table.
        conn.execute(
            """
            INSERT INTO chunks_fts(rowid, title, body, aliases, screen, component, raw_tags)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                row_id,
                doc.title,
                doc.body,
                " ".join(doc.aliases),
                doc.screen or "",
                doc.component or "",
                " ".join(doc.raw_tags),
            ),
        )
        count += 1

    conn.commit()
    conn.close()
    return count


if __name__ == "__main__":
    target_path = get_default_db_path()
    if target_path == FALLBACK_DB_PATH:
        target_path = make_temp_db_path("drillbot_ingest")
    total = rebuild_database(db_path=target_path)
    print(f"Ingested {total} markdown chunks into {target_path}")
