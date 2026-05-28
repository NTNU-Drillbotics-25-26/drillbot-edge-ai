from __future__ import annotations

import sqlite3
import tempfile
from pathlib import Path
import os


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
DEFAULT_DB_PATH = DATA_DIR / "drillbot.db"
FALLBACK_DB_PATH = Path(tempfile.gettempdir()) / "drillbot.db"


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS chunks (
    id INTEGER PRIMARY KEY,
    doc_id TEXT UNIQUE,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    aliases TEXT,
    screen TEXT,
    component TEXT,
    raw_tags TEXT,
    status TEXT NOT NULL,
    source_type TEXT,
    historic INTEGER NOT NULL DEFAULT 0
);

CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
    title,
    body,
    aliases,
    screen,
    component,
    raw_tags,
    content='chunks',
    content_rowid='id'
);
"""


def get_default_db_path() -> Path:
    override = os.environ.get("DRILLBOT_DB_PATH")
    if override:
        return Path(override)
    # OneDrive-backed folders have been unreliable for SQLite in this workspace,
    # so local development falls back to a temp DB unless explicitly overridden.
    if "OneDrive" in str(DEFAULT_DB_PATH):
        return FALLBACK_DB_PATH
    return DEFAULT_DB_PATH


def make_temp_db_path(prefix: str = "drillbot") -> Path:
    return Path(tempfile.gettempdir()) / f"{prefix}_{os.getpid()}.db"


def _connect(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    # Keep SQLite temp/journal files in memory to reduce sync-folder issues.
    conn.execute("PRAGMA journal_mode=MEMORY")
    conn.execute("PRAGMA temp_store=MEMORY")
    return conn


def get_connection(db_path: Path | None = None) -> sqlite3.Connection:
    path = Path(db_path or get_default_db_path())
    try:
        return _connect(path)
    except sqlite3.OperationalError:
        if db_path is not None:
            raise
        return _connect(FALLBACK_DB_PATH)


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA_SQL)
    conn.commit()
