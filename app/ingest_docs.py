"""Ingest design documents into vector store for embedding-based retrieval.

Supports PDF and DOCX files organized by year in the documents/ directory.
Uses ChromaDB for vector storage and Ollama for embeddings.

Usage:
    python -m scripts.ingest_documents
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Iterator

import chromadb
import requests

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parents[1]
DOCUMENTS_DIR = BASE_DIR / "documents"
CHROMA_PATH = BASE_DIR / "data" / "chroma"

# Ollama embedding settings
OLLAMA_EMBED_URL = "http://localhost:11434/api/embeddings"
EMBED_MODEL = "nomic-embed-text"

# Chunking settings
CHUNK_SIZE = 250  # words per chunk (reduced from 400 for more precise retrieval)
CHUNK_OVERLAP = 40  # overlap between chunks (reduced from 50)

# Citation patterns to remove from text (references already removed manually)
CITATION_PATTERNS = [
    re.compile(r'\[\d+(?:,\s*\d+)*\]'),  # [1], [1, 2, 3]
    re.compile(r'\([A-Z][a-z]+(?:\s+et\s+al\.?)?,?\s*\d{4}\)'),  # (Author et al., 2024)
]

# Heading patterns for structure detection (order matters: most specific first)
# These patterns are designed to match academic thesis/report headings
HEADING_PATTERNS = [
    # "Chapter 1: Introduction" or "Chapter 1 Introduction"
    (1, re.compile(r'^Chapter\s*(\d+)[:\.\s]+\s*(.+)$', re.IGNORECASE)),
    # "1.1.1.1 Sub-sub-subsection" (rare but possible)
    (4, re.compile(r'^(\d+\.\d+\.\d+\.\d+)\s+([A-Z][A-Za-z].{2,})$')),
    # "1.1.1 Subsection Title" - must start with letter after numbers
    (3, re.compile(r'^(\d+\.\d+\.\d+)\s+([A-Z][A-Za-z].{2,})$')),
    # "1.1 Section Title" - must start with letter after numbers, allow mixed case
    (2, re.compile(r'^(\d+\.\d+)\s+([A-Z][A-Za-z].{2,})$')),
    # "1 Introduction" - single/double digit + proper title
    (1, re.compile(r'^(\d{1,2})\s+([A-Z][a-z]{2,}(?:\s+[A-Za-z]+)*)$')),
    # ALL CAPS chapter titles - minimum 8 chars, at least 2 words OR one long word
    # This avoids abbreviations like "IDBHA", "OPC UA"
    (1, re.compile(r'^([A-Z]{8,}|[A-Z]{2,}\s+[A-Z]{2,}(?:\s+[A-Z]{2,})*)$')),
]

# Patterns for split-line headings (number on one line, title on next)
# These return (level, number_str) for later combination with title
SPLIT_HEADING_NUMBER_PATTERNS = [
    (4, re.compile(r'^(\d+\.\d+\.\d+\.\d+)$')),  # 1.1.1.1
    (3, re.compile(r'^(\d+\.\d+\.\d+)$')),        # 1.1.1
    (2, re.compile(r'^(\d+\.\d+)$')),              # 1.1
    (1, re.compile(r'^(\d{1,2})$')),               # 1 or 12
]

# Known abbreviations and short terms to reject as headings
HEADING_REJECT_TERMS = {
    'ID', 'OD', 'BHA', 'DP', 'WOB', 'ROP', 'RPM', 'API', 'OPC', 'UA', 'PLC',
    'NTNU', 'SPE', 'PDF', 'CAD', 'FEM', 'CFD', 'GUI', 'HMI', 'PID', 'MPC',
    'IDBHA', 'ODBHA', 'IDOD', 'ODID',
}

# Noise patterns to reject (tables, equations, units, etc.)
HEADING_NOISE_PATTERNS = [
    re.compile(r'[<>=≤≥±·×÷∙]'),  # Math operators
    re.compile(r'\b(?:Nm|kW|kg|mm|cm|m|ft|lbs?|RPM|Hz|Pa|MPa|GPa|psi)\b', re.IGNORECASE),  # Units
    re.compile(r'\b\d+[.,]\d+\b'),  # Decimal numbers (likely values, not headings)
    re.compile(r'^\s*[\d.,\s]+$'),  # Lines of only numbers
    re.compile(r'\b(?:Table|Figure|Fig\.|Equation|Eq\.)\s*\d', re.IGNORECASE),  # Captions
    re.compile(r'^\s*\([a-z]\)'),  # List items like (a), (b)
    re.compile(r'[{}\\$]'),  # LaTeX artifacts
]

# Known good heading keywords (boost detection confidence)
HEADING_KEYWORDS = {
    'introduction', 'background', 'motivation', 'objectives', 'scope',
    'literature', 'review', 'theory', 'theoretical',
    'methodology', 'methods', 'method', 'approach', 'design',
    'implementation', 'system', 'architecture', 'hardware', 'software',
    'results', 'analysis', 'discussion', 'evaluation', 'testing',
    'conclusion', 'conclusions', 'summary', 'future', 'work',
    'references', 'bibliography', 'appendix', 'appendices',
    'abstract', 'acknowledgements', 'acknowledgments',
    'drilling', 'control', 'sensor', 'automation', 'algorithm',
}

# Page artifact patterns to remove (headers, footers, page numbers)
PAGE_ARTIFACT_PATTERNS = [
    # Standalone page numbers
    re.compile(r'^\s*\d{1,3}\s*$', re.MULTILINE),
    # "Page X" or "Page X of Y"
    re.compile(r'^\s*Page\s+\d+(\s+of\s+\d+)?\s*$', re.MULTILINE | re.IGNORECASE),
    # Roman numerals alone (often in front matter)
    re.compile(r'^\s*[ivxlcm]+\s*$', re.MULTILINE | re.IGNORECASE),
    # Common running headers - university/competition names
    re.compile(r'^\s*(NTNU|Norwegian University|Drillbotics|SPE)\s*$', re.MULTILINE | re.IGNORECASE),
    # Year markers alone
    re.compile(r'^\s*20[12]\d\s*$', re.MULTILINE),
    # Chapter/section references in headers like "Chapter 3" or "3. Methodology" alone on a line
    re.compile(r'^\s*Chapter\s+\d+\s*$', re.MULTILINE | re.IGNORECASE),
    # Repeated short lines that are likely headers (e.g., "MECHANICAL RIG DESIGN" repeated)
    # This is handled separately in clean_page_artifacts()
]

# Lines that look like running headers when short and repeated
RUNNING_HEADER_MAX_WORDS = 6

# Structural chunking settings
STRUCT_CHUNK_MAX_WORDS = 400  # Max words per structural chunk
STRUCT_CHUNK_MIN_WORDS = 50   # Min words to keep a chunk


@dataclass
class StructuralNode:
    """A node in the document structure tree."""
    level: int  # 0=root, 1=chapter, 2=section, 3=subsection, 4=paragraph
    title: str
    content: str  # Text content (excluding children)
    children: list["StructuralNode"] = field(default_factory=list)
    page_start: int | None = None
    page_end: int | None = None

    def word_count(self) -> int:
        """Total words in this node and all children."""
        own = len(self.content.split()) if self.content else 0
        return own + sum(c.word_count() for c in self.children)

    def __repr__(self) -> str:
        return f"StructuralNode(level={self.level}, title='{self.title[:30]}...', words={self.word_count()})"


class OllamaEmbeddingFunction:
    """ChromaDB-compatible embedding function using Ollama."""

    def __init__(self, model: str = EMBED_MODEL, url: str = OLLAMA_EMBED_URL):
        self._model = model
        self._url = url

    def name(self) -> str:
        """Return embedding function name (required by ChromaDB)."""
        return f"ollama/{self._model}"

    def _embed_single(self, text: str) -> list[float]:
        """Generate embedding for a single text."""
        try:
            response = requests.post(
                self._url,
                json={"model": self._model, "prompt": text},
                timeout=30,
            )
            response.raise_for_status()
            return response.json().get("embedding", [0.0] * 768)
        except Exception as e:
            logger.error(f"Embedding error: {e}")
            return [0.0] * 768

    def __call__(self, input: list[str]) -> list[list[float]]:
        """Generate embeddings for a list of texts (used for document ingestion)."""
        return [self._embed_single(text) for text in input]

    def embed_documents(self, documents: list[str]) -> list[list[float]]:
        """Alias for __call__ (ChromaDB compatibility)."""
        return self(documents)

    def embed_query(self, query=None, input=None) -> list[list[float]]:
        """Generate embedding for a query (used for retrieval)."""
        # Handle both string and list inputs from ChromaDB
        text = query or input or ""
        if isinstance(text, list):
            text = text[0] if text else ""
        if not text or not str(text).strip():
            return [[0.0] * 768]
        return [self._embed_single(str(text))]


def get_chroma_client() -> chromadb.PersistentClient:
    """Get or create ChromaDB persistent client."""
    CHROMA_PATH.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(CHROMA_PATH))


def get_collection(client: chromadb.PersistentClient | None = None):
    """Get or create the design_docs collection."""
    if client is None:
        client = get_chroma_client()

    return client.get_or_create_collection(
        name="design_docs",
        embedding_function=OllamaEmbeddingFunction(),
        metadata={"hnsw:space": "cosine"},
    )


def extract_text_from_pdf(path: Path) -> str:
    """Extract text from a PDF file using PyMuPDF."""
    try:
        import fitz  # PyMuPDF
    except ImportError:
        raise ImportError("PyMuPDF not installed. Run: pip install pymupdf")

    doc = fitz.open(path)
    text_parts = []
    for page in doc:
        text_parts.append(page.get_text())
    doc.close()
    return "\n".join(text_parts)


def extract_pdf_with_pages(path: Path) -> list[tuple[str, int]]:
    """Extract text with page numbers. Returns [(text, page_num), ...]"""
    try:
        import fitz  # PyMuPDF
    except ImportError:
        raise ImportError("PyMuPDF not installed. Run: pip install pymupdf")

    doc = fitz.open(path)
    pages = []
    for page_num, page in enumerate(doc, start=1):
        text = page.get_text().strip()
        if text:
            pages.append((text, page_num))
    doc.close()
    return pages


def clean_citations(text: str) -> str:
    """Remove inline citations that cause hallucination."""
    for pattern in CITATION_PATTERNS:
        text = pattern.sub('', text)
    return text


def get_doc_type(path: Path) -> str:
    """Determine document type from path."""
    path_str = str(path).lower()
    if "rule" in path_str:
        return "rules"
    elif "thesis" in path_str:
        return "thesis"
    elif "report" in path_str:
        return "report"
    return "document"


def extract_text_from_docx(path: Path) -> str:
    """Extract text from a DOCX file."""
    try:
        from docx import Document
    except ImportError:
        raise ImportError("python-docx not installed. Run: pip install python-docx")

    doc = Document(path)
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)


def extract_text(path: Path) -> str | None:
    """Extract text from a document based on file extension."""
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        return extract_text_from_pdf(path)
    elif suffix == ".docx":
        return extract_text_from_docx(path)
    elif suffix == ".txt":
        return path.read_text(encoding="utf-8")
    elif suffix == ".md":
        return path.read_text(encoding="utf-8")
    else:
        logger.warning(f"Unsupported file type: {path}")
        return None


def clean_text(text: str) -> str:
    """Clean extracted text for better chunking."""
    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)
    # Remove excessive newlines
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def clean_page_artifacts(text: str) -> str:
    """
    Remove page headers, footers, and page numbers from extracted PDF text.

    These artifacts appear mid-sentence when text spans pages and confuse LLMs.
    """
    # Apply basic artifact patterns
    for pattern in PAGE_ARTIFACT_PATTERNS:
        text = pattern.sub('', text)

    # Find and remove repeated short lines (likely running headers)
    lines = text.split('\n')
    line_counts: dict[str, int] = {}

    for line in lines:
        stripped = line.strip()
        if stripped and len(stripped.split()) <= RUNNING_HEADER_MAX_WORDS:
            normalized = stripped.upper()
            line_counts[normalized] = line_counts.get(normalized, 0) + 1

    # Lines that appear 3+ times and are short are likely headers
    repeated_headers = {
        line for line, count in line_counts.items()
        if count >= 3 and len(line.split()) <= RUNNING_HEADER_MAX_WORDS
    }

    # Remove the repeated headers
    if repeated_headers:
        cleaned_lines = []
        for line in lines:
            stripped = line.strip().upper()
            if stripped not in repeated_headers:
                cleaned_lines.append(line)
        text = '\n'.join(cleaned_lines)

    # Clean up artifacts that appear mid-sentence (page breaks)
    # Pattern: sentence fragment, newline, page number/header, newline, continuation
    # Fix hyphenated words split across pages: "drill-\n\n52\n\ning" -> "drilling"
    text = re.sub(r'-\s*\n\s*\d{1,3}\s*\n\s*', '', text)

    # Remove orphaned page numbers between paragraphs
    text = re.sub(r'\n\s*\d{1,3}\s*\n', '\n', text)

    # Normalize multiple newlines created by removals
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text.strip()


def extract_pdf_text_clean(path: Path) -> str:
    """Extract and clean text from PDF, removing page artifacts."""
    try:
        import fitz  # PyMuPDF
    except ImportError:
        raise ImportError("PyMuPDF not installed. Run: pip install pymupdf")

    doc = fitz.open(path)
    text_parts = []

    for page in doc:
        page_text = page.get_text()
        text_parts.append(page_text)

    doc.close()

    # Join with markers, then clean
    full_text = "\n".join(text_parts)
    full_text = clean_page_artifacts(full_text)
    full_text = clean_citations(full_text)

    return full_text


def extract_pdf_pages_clean(path: Path) -> list[tuple[str, int]]:
    """Extract text with page numbers, cleaning artifacts from each page."""
    try:
        import fitz  # PyMuPDF
    except ImportError:
        raise ImportError("PyMuPDF not installed. Run: pip install pymupdf")

    doc = fitz.open(path)
    pages = []

    # First pass: collect all page text to find repeated headers
    all_text = []
    for page in doc:
        all_text.append(page.get_text())

    # Find repeated short lines across the document
    line_counts: dict[str, int] = {}
    for page_text in all_text:
        seen_on_page: set[str] = set()
        for line in page_text.split('\n'):
            stripped = line.strip()
            if stripped and len(stripped.split()) <= RUNNING_HEADER_MAX_WORDS:
                normalized = stripped.upper()
                if normalized not in seen_on_page:
                    seen_on_page.add(normalized)
                    line_counts[normalized] = line_counts.get(normalized, 0) + 1

    # Headers appear on multiple consecutive pages (3+ times is suspicious)
    # Lower threshold to catch chapter headers that only span part of document
    min_occurrences = 3
    repeated_headers = {
        line for line, count in line_counts.items()
        if count >= min_occurrences
    }

    # Track which headers we've seen (to keep first occurrence)
    seen_headers: set[str] = set()

    # Second pass: extract and clean each page
    for page_num, page_text in enumerate(all_text, start=1):
        # Remove repeated headers (but keep first occurrence)
        lines = page_text.split('\n')
        cleaned_lines = []
        for line in lines:
            stripped = line.strip().upper()
            if stripped in repeated_headers:
                if stripped not in seen_headers:
                    # First occurrence - keep it
                    seen_headers.add(stripped)
                    cleaned_lines.append(line)
                # else: skip this repeated header
            else:
                cleaned_lines.append(line)

        cleaned_text = '\n'.join(cleaned_lines)

        # Apply other cleaning
        for pattern in PAGE_ARTIFACT_PATTERNS:
            cleaned_text = pattern.sub('', cleaned_text)

        cleaned_text = clean_citations(cleaned_text)
        cleaned_text = cleaned_text.strip()

        if cleaned_text:
            pages.append((cleaned_text, page_num))

    doc.close()
    return pages


def chunk_text(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> list[str]:
    """Split text into overlapping chunks by word count."""
    words = text.split()
    chunks = []

    if len(words) <= chunk_size:
        return [text] if text.strip() else []

    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        if chunk.strip():
            chunks.append(chunk)
        start = end - overlap

    return chunks


def chunk_with_pages(
    pages: list[tuple[str, int]],
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> list[tuple[str, int, int]]:
    """Chunk text while tracking page ranges. Returns [(chunk, page_start, page_end), ...]"""
    chunks = []
    current_words = []
    current_pages: set[int] = set()

    for text, page_num in pages:
        text = clean_citations(text)  # Remove inline citations
        words = text.split()

        for word in words:
            current_words.append(word)
            current_pages.add(page_num)

            if len(current_words) >= chunk_size:
                chunk_text = " ".join(current_words)
                chunks.append((chunk_text, min(current_pages), max(current_pages)))
                # Overlap: keep last N words
                current_words = current_words[-overlap:]
                current_pages = {max(current_pages)}

    # Final chunk if has enough content
    if len(current_words) >= 30:
        chunk_text = " ".join(current_words)
        chunks.append((chunk_text, min(current_pages), max(current_pages)))

    return chunks


# =============================================================================
# HIERARCHICAL STRUCTURE-AWARE CHUNKING
# =============================================================================


def _is_heading_noise(line: str) -> bool:
    """Check if a line contains noise patterns (equations, units, table content)."""
    for pattern in HEADING_NOISE_PATTERNS:
        if pattern.search(line):
            return True
    return False


def _has_heading_keyword(text: str) -> bool:
    """Check if text contains known heading keywords."""
    words = set(text.lower().split())
    return bool(words & HEADING_KEYWORDS)


def _detect_heading(line: str) -> tuple[int, str] | None:
    """
    Detect if a line is a heading and return (level, title).
    Returns None if not a heading.

    Uses strict validation to avoid detecting table content, equations, etc.
    """
    line = line.strip()

    # Basic length checks
    if not line or len(line) > 80 or len(line) < 5:
        return None

    # Reject lines with noise (equations, units, numbers)
    if _is_heading_noise(line):
        return None

    # Reject known abbreviations
    line_upper = line.upper().replace(' ', '')
    if line_upper in HEADING_REJECT_TERMS or line.upper() in HEADING_REJECT_TERMS:
        return None

    # Reject if all words are abbreviations
    words = line.split()
    if all(w.upper() in HEADING_REJECT_TERMS for w in words):
        return None

    # Try each heading pattern
    for level, pattern in HEADING_PATTERNS:
        match = pattern.match(line)
        if match:
            # Extract title from the appropriate group
            if match.lastindex and match.lastindex >= 2:
                title = match.group(2).strip()
            else:
                title = match.group(1).strip() if match.lastindex else line

            # Validate the title
            if len(title) < 5:
                continue

            # Title should have mostly letters (not numbers/symbols)
            letter_ratio = sum(1 for c in title if c.isalpha()) / len(title)
            if letter_ratio < 0.7:
                continue

            # Reject if title is just abbreviations
            title_words = title.split()
            if all(w.upper() in HEADING_REJECT_TERMS for w in title_words):
                continue

            return (level, title)

    return None


def _detect_split_heading_number(line: str) -> tuple[int, str] | None:
    """
    Detect if a line is just a section number (e.g., "6.1", "6.5.2").
    Returns (level, number_str) if it's a standalone section number.
    """
    line = line.strip()

    # Must be short (just a number)
    if not line or len(line) > 10:
        return None

    for level, pattern in SPLIT_HEADING_NUMBER_PATTERNS:
        match = pattern.match(line)
        if match:
            num_str = match.group(1)

            # Reject if it looks like a monetary value or measurement
            # Real section numbers have small integers (1-20ish), not 109.6 or 377.5
            parts = num_str.split('.')
            try:
                # First number should be reasonable chapter number (1-20)
                first_num = int(parts[0])
                if first_num > 20:
                    return None

                # Subsection numbers should also be small (1-15ish)
                for part in parts[1:]:
                    if int(part) > 15:
                        return None

            except ValueError:
                return None

            return (level, num_str)

    return None


def _is_valid_split_title(line: str) -> bool:
    """Check if a line could be a title following a section number."""
    line = line.strip()

    if not line or len(line) < 3 or len(line) > 80:
        return False

    # Should start with capital letter
    if not line[0].isupper():
        return False

    # Should be mostly letters
    letter_ratio = sum(1 for c in line if c.isalpha()) / len(line)
    if letter_ratio < 0.7:
        return False

    # Should not be noise
    if _is_heading_noise(line):
        return False

    # Should not be just abbreviations
    words = line.split()
    if all(w.upper() in HEADING_REJECT_TERMS for w in words):
        return False

    return True


def parse_structure(
    text: str,
    pages: list[tuple[str, int]] | None = None,
) -> StructuralNode:
    """
    Parse document text into a hierarchical structure tree.

    Handles both single-line headings ("1.1 Title") and split-line headings
    where the number is on one line and the title on the next:
        6.1
        Section Title

    Args:
        text: Full document text
        pages: Optional list of (page_text, page_num) for page tracking

    Returns:
        Root StructuralNode containing the document tree
    """
    root = StructuralNode(level=0, title="Document", content="")
    current_stack = [root]  # Stack of ancestor nodes
    seen_headings: set[tuple[int, str]] = set()  # Track (level, title) to dedupe

    lines = text.split('\n')
    i = 0

    def add_heading(level: int, title: str):
        """Add a heading node to the tree."""
        heading_key = (level, title.upper())

        # Skip if we've already seen this heading (running header)
        if heading_key in seen_headings:
            return

        seen_headings.add(heading_key)
        node = StructuralNode(level=level, title=title, content="")

        # Pop stack until we find appropriate parent (lower level number)
        while len(current_stack) > 1 and current_stack[-1].level >= level:
            current_stack.pop()

        current_stack[-1].children.append(node)
        current_stack.append(node)

    def add_content(text: str):
        """Add content to the current section."""
        text = text.strip()
        if not text:
            return
        current_node = current_stack[-1]
        if current_node.content:
            current_node.content += "\n\n" + text
        else:
            current_node.content = text

    content_buffer = []

    while i < len(lines):
        line = lines[i].strip()

        if not line:
            # Empty line - might end a paragraph
            if content_buffer:
                add_content(' '.join(content_buffer))
                content_buffer = []
            i += 1
            continue

        # Check for single-line heading
        heading = _detect_heading(line)
        if heading:
            # Flush any buffered content
            if content_buffer:
                add_content(' '.join(content_buffer))
                content_buffer = []
            add_heading(heading[0], heading[1])
            i += 1
            continue

        # Check for split-line heading (number on this line, title on next)
        split_num = _detect_split_heading_number(line)
        if split_num:
            level, num_str = split_num

            # Look ahead for title on next non-empty line
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1

            if j < len(lines):
                potential_title = lines[j].strip()
                if _is_valid_split_title(potential_title):
                    # Found a split heading!
                    if content_buffer:
                        add_content(' '.join(content_buffer))
                        content_buffer = []

                    # Combine number and title
                    full_title = f"{num_str} {potential_title}"
                    add_heading(level, full_title)
                    i = j + 1  # Skip past the title line
                    continue

        # Regular content line
        content_buffer.append(line)
        i += 1

    # Flush remaining content
    if content_buffer:
        add_content(' '.join(content_buffer))

    return root


def _flatten_node(node: StructuralNode, include_title: bool = True) -> str:
    """Flatten a node and all children into text."""
    parts = []

    if include_title and node.title and node.level > 0:
        # Add heading with markdown-style markers for context
        parts.append(f"{'#' * node.level} {node.title}")

    if node.content:
        parts.append(node.content)

    for child in node.children:
        parts.append(_flatten_node(child, include_title=True))

    return "\n\n".join(filter(None, parts))


def _split_by_sentences(
    text: str,
    max_words: int,
    min_words: int,
) -> Iterator[str]:
    """
    Last-resort splitting by sentences when structural units are too large.
    """
    # Split on sentence boundaries
    sentences = re.split(r'(?<=[.!?])\s+', text)
    current_chunk = []
    current_count = 0

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        words = len(sentence.split())

        # If adding this sentence exceeds limit and we have content, yield
        if current_count + words > max_words and current_chunk:
            yield " ".join(current_chunk)
            current_chunk = []
            current_count = 0

        current_chunk.append(sentence)
        current_count += words

    # Yield remaining if meets minimum
    if current_chunk and current_count >= min_words:
        yield " ".join(current_chunk)
    elif current_chunk:
        # Below minimum but still yield to not lose content
        yield " ".join(current_chunk)


def chunk_structural(
    node: StructuralNode,
    max_words: int = STRUCT_CHUNK_MAX_WORDS,
    min_words: int = STRUCT_CHUNK_MIN_WORDS,
    heading_path: list[str] | None = None,
) -> Iterator[dict]:
    """
    Recursively chunk a structural node, respecting document boundaries.

    Strategy:
    1. If node (with children) fits within max_words → emit as single chunk
    2. If node exceeds limit → emit own content, then recurse into children
    3. If leaf content still too large → split by sentences

    Yields:
        dict with keys: text, heading_path, level, title
    """
    heading_path = heading_path or []
    current_path = heading_path + [node.title] if node.title and node.level > 0 else heading_path

    total_words = node.word_count()

    # Case 1: Entire node (including children) fits - emit as single chunk
    if total_words <= max_words and total_words >= min_words:
        full_text = _flatten_node(node)
        if full_text.strip():
            yield {
                "text": full_text,
                "heading_path": " > ".join(current_path) if current_path else "Document",
                "level": node.level,
                "title": node.title or "Document",
            }
        return

    # Case 2: Node too small - still emit if has content (don't lose data)
    if total_words < min_words and total_words > 0:
        full_text = _flatten_node(node)
        if full_text.strip():
            yield {
                "text": full_text,
                "heading_path": " > ".join(current_path) if current_path else "Document",
                "level": node.level,
                "title": node.title or "Document",
            }
        return

    # Case 3: Node too large - split into own content + children
    if node.content:
        content_words = len(node.content.split())
        content_with_title = f"{'#' * node.level} {node.title}\n\n{node.content}" if node.title and node.level > 0 else node.content

        if content_words <= max_words:
            # Content fits as one chunk
            if content_words >= min_words:
                yield {
                    "text": content_with_title,
                    "heading_path": " > ".join(current_path) if current_path else "Document",
                    "level": node.level,
                    "title": node.title or "Document",
                }
            elif content_words > 0:
                # Below min but emit anyway
                yield {
                    "text": content_with_title,
                    "heading_path": " > ".join(current_path) if current_path else "Document",
                    "level": node.level,
                    "title": node.title or "Document",
                }
        else:
            # Content too large - split by sentences
            first_chunk = True
            for chunk in _split_by_sentences(node.content, max_words, min_words):
                # Include title only in first chunk
                if first_chunk and node.title and node.level > 0:
                    chunk = f"{'#' * node.level} {node.title}\n\n{chunk}"
                    first_chunk = False

                yield {
                    "text": chunk,
                    "heading_path": " > ".join(current_path) if current_path else "Document",
                    "level": node.level,
                    "title": node.title or "Document",
                }

    # Recurse into children
    for child in node.children:
        yield from chunk_structural(child, max_words, min_words, current_path)


def chunk_thesis_structured(
    text: str,
    max_words: int = STRUCT_CHUNK_MAX_WORDS,
    min_words: int = STRUCT_CHUNK_MIN_WORDS,
) -> list[tuple[str, dict]]:
    """
    Structure-aware chunking for thesis/academic documents.

    Args:
        text: Full document text
        max_words: Maximum words per chunk
        min_words: Minimum words per chunk

    Returns:
        List of (chunk_text, metadata_dict) tuples
    """
    # Clean text first
    text = clean_citations(text)

    # Parse into structure tree
    root = parse_structure(text)

    # Log structure info
    logger.info(f"  Parsed structure: {_count_nodes(root)} sections detected")

    # Generate chunks respecting structure
    chunks = []
    for chunk_data in chunk_structural(root, max_words, min_words):
        metadata = {
            "heading_path": chunk_data["heading_path"],
            "structural_level": chunk_data["level"],
            "section_title": chunk_data["title"],
        }
        chunks.append((chunk_data["text"], metadata))

    return chunks


def _count_nodes(node: StructuralNode) -> int:
    """Count total nodes in tree (for logging)."""
    return 1 + sum(_count_nodes(c) for c in node.children)


def chunk_pdf_structured(
    pages: list[tuple[str, int]],
    max_words: int = STRUCT_CHUNK_MAX_WORDS,
    min_words: int = STRUCT_CHUNK_MIN_WORDS,
) -> list[tuple[str, dict, int, int]]:
    """
    Structure-aware chunking for PDF with page tracking.

    Args:
        pages: List of (page_text, page_num) tuples (should be pre-cleaned)
        max_words: Maximum words per chunk
        min_words: Minimum words per chunk

    Returns:
        List of (chunk_text, struct_metadata, page_start, page_end) tuples
    """
    # Combine all pages into single text (we'll estimate page ranges)
    full_text = "\n\n".join(text for text, _ in pages)
    page_numbers = [num for _, num in pages]
    page_starts = {}

    # Build a rough word-position to page mapping
    word_count = 0
    for text, page_num in pages:
        page_starts[word_count] = page_num
        word_count += len(text.split())

    # Parse structure (text should already be cleaned)
    root = parse_structure(full_text)

    logger.info(f"  Parsed structure: {_count_nodes(root)} sections detected")

    # Generate chunks
    chunks = []
    cumulative_words = 0

    for chunk_data in chunk_structural(root, max_words, min_words):
        chunk_text = chunk_data["text"]
        chunk_words = len(chunk_text.split())

        # Estimate page range based on word position
        page_start = page_numbers[0] if page_numbers else 1
        page_end = page_numbers[-1] if page_numbers else 1

        # Find approximate page for this chunk's position
        for word_pos, page_num in sorted(page_starts.items()):
            if word_pos <= cumulative_words:
                page_start = page_num
            if word_pos <= cumulative_words + chunk_words:
                page_end = page_num

        cumulative_words += chunk_words

        metadata = {
            "heading_path": chunk_data["heading_path"],
            "structural_level": chunk_data["level"],
            "section_title": chunk_data["title"],
        }
        chunks.append((chunk_text, metadata, page_start, page_end))

    return chunks


def extract_year_from_path(path: Path) -> int:
    """Extract year from path like documents/2025/report.pdf."""
    # Check folder names for year
    for part in path.parts:
        if part.isdigit() and 2000 <= int(part) <= 2100:
            return int(part)

    # Check filename for year pattern
    match = re.search(r"20\d{2}", path.stem)
    if match:
        return int(match.group())

    # Default to current year
    return datetime.now().year


def iter_documents(docs_dir: Path = DOCUMENTS_DIR) -> Iterator[Path]:
    """Iterate over all supported documents in the directory."""
    if not docs_dir.exists():
        logger.warning(f"Documents directory does not exist: {docs_dir}")
        return

    supported = {".pdf", ".docx", ".txt", ".md"}
    for path in sorted(docs_dir.rglob("*")):
        if path.is_file() and path.suffix.lower() in supported:
            yield path


def _clean_metadata(meta: dict) -> dict:
    """Clean metadata dict for ChromaDB - remove None values."""
    cleaned = {}
    for key, value in meta.items():
        if value is None:
            # ChromaDB doesn't accept None - use empty string or skip
            cleaned[key] = ""
        else:
            cleaned[key] = value
    return cleaned


def ingest_documents(
    docs_dir: Path = DOCUMENTS_DIR,
    clear_existing: bool = True,
) -> int:
    """
    Ingest all documents from the documents directory into ChromaDB.

    Args:
        docs_dir: Directory containing documents organized by year
        clear_existing: Whether to clear existing embeddings first

    Returns:
        Number of chunks indexed
    """
    client = get_chroma_client()
    collection = get_collection(client)

    # Clear existing documents if requested
    if clear_existing:
        existing = collection.get()
        if existing["ids"]:
            logger.info(f"Clearing {len(existing['ids'])} existing chunks")
            collection.delete(ids=existing["ids"])

    all_chunks = []
    all_ids = []
    all_metadatas = []

    for path in iter_documents(docs_dir):
        logger.info(f"Processing: {path.name}")

        year = extract_year_from_path(path)
        doc_type = get_doc_type(path)
        use_structural = doc_type in ("thesis", "report")  # Use structural chunking for academic docs

        # PDF files
        if path.suffix.lower() == ".pdf":
            # Use cleaned extraction for structural chunking (removes page headers/footers)
            if use_structural:
                pages = extract_pdf_pages_clean(path)
            else:
                pages = extract_pdf_with_pages(path)

            if not pages:
                continue

            if use_structural:
                # Structure-aware chunking for thesis/reports
                logger.info(f"  Using STRUCTURAL chunking for {doc_type}")
                struct_chunks = chunk_pdf_structured(pages)
                logger.info(f"  Year: {year}, Type: {doc_type}, Chunks: {len(struct_chunks)}")

                for i, (chunk_text_content, struct_meta, page_start, page_end) in enumerate(struct_chunks):
                    chunk_id = f"{path.stem}_{year}_{i:04d}"
                    all_chunks.append(chunk_text_content)
                    all_ids.append(chunk_id)
                    all_metadatas.append(_clean_metadata({
                        "source": path.name,
                        "source_path": str(path.relative_to(docs_dir)),
                        "year": year,
                        "chunk_index": i,
                        "total_chunks": len(struct_chunks),
                        "doc_type": doc_type,
                        "page_start": page_start,
                        "page_end": page_end,
                        # Structural metadata
                        "heading_path": struct_meta.get("heading_path"),
                        "structural_level": struct_meta.get("structural_level"),
                        "section_title": struct_meta.get("section_title"),
                    }))
            else:
                # Fixed-size chunking for rules and other docs
                page_chunks = chunk_with_pages(pages)
                logger.info(f"  Year: {year}, Type: {doc_type}, Chunks: {len(page_chunks)}")

                for i, (chunk_text_content, page_start, page_end) in enumerate(page_chunks):
                    chunk_id = f"{path.stem}_{year}_{i:04d}"
                    all_chunks.append(chunk_text_content)
                    all_ids.append(chunk_id)
                    all_metadatas.append(_clean_metadata({
                        "source": path.name,
                        "source_path": str(path.relative_to(docs_dir)),
                        "year": year,
                        "chunk_index": i,
                        "total_chunks": len(page_chunks),
                        "doc_type": doc_type,
                        "page_start": page_start,
                        "page_end": page_end,
                        "heading_path": None,
                        "structural_level": None,
                        "section_title": None,
                    }))
        else:
            # Non-PDF files
            text = extract_text(path)
            if not text:
                continue

            if use_structural:
                # Structure-aware chunking for thesis/reports (DOCX, MD, TXT)
                logger.info(f"  Using STRUCTURAL chunking for {doc_type}")
                text = clean_text(text)
                struct_chunks = chunk_thesis_structured(text)
                logger.info(f"  Year: {year}, Type: {doc_type}, Chunks: {len(struct_chunks)}")

                for i, (chunk_text_content, struct_meta) in enumerate(struct_chunks):
                    chunk_id = f"{path.stem}_{year}_{i:04d}"
                    all_chunks.append(chunk_text_content)
                    all_ids.append(chunk_id)
                    all_metadatas.append(_clean_metadata({
                        "source": path.name,
                        "source_path": str(path.relative_to(docs_dir)),
                        "year": year,
                        "chunk_index": i,
                        "total_chunks": len(struct_chunks),
                        "doc_type": doc_type,
                        "page_start": None,
                        "page_end": None,
                        "heading_path": struct_meta.get("heading_path"),
                        "structural_level": struct_meta.get("structural_level"),
                        "section_title": struct_meta.get("section_title"),
                    }))
            else:
                # Fixed-size chunking for rules and other docs
                text = clean_text(text)
                text = clean_citations(text)
                chunks = chunk_text(text)

                logger.info(f"  Year: {year}, Type: {doc_type}, Chunks: {len(chunks)}")

                for i, chunk in enumerate(chunks):
                    chunk_id = f"{path.stem}_{year}_{i:04d}"
                    all_chunks.append(chunk)
                    all_ids.append(chunk_id)
                    all_metadatas.append(_clean_metadata({
                        "source": path.name,
                        "source_path": str(path.relative_to(docs_dir)),
                        "year": year,
                        "chunk_index": i,
                        "total_chunks": len(chunks),
                        "doc_type": doc_type,
                        "page_start": None,
                        "page_end": None,
                        "heading_path": None,
                        "structural_level": None,
                        "section_title": None,
                    }))

    if not all_chunks:
        logger.warning("No documents found to ingest")
        return 0

    # Batch insert (ChromaDB handles batching internally)
    logger.info(f"Inserting {len(all_chunks)} chunks into ChromaDB...")

    # Process in batches to avoid memory issues
    batch_size = 50
    for i in range(0, len(all_chunks), batch_size):
        end = min(i + batch_size, len(all_chunks))
        collection.add(
            documents=all_chunks[i:end],
            ids=all_ids[i:end],
            metadatas=all_metadatas[i:end],
        )
        logger.info(f"  Indexed {end}/{len(all_chunks)} chunks")

    return len(all_chunks)


def get_document_stats() -> dict:
    """Get statistics about indexed documents."""
    try:
        collection = get_collection()
        all_data = collection.get(include=["metadatas"])

        if not all_data["ids"]:
            return {"total_chunks": 0, "documents": [], "years": []}

        sources = set()
        years = set()
        for meta in all_data["metadatas"]:
            sources.add(meta.get("source", "unknown"))
            years.add(meta.get("year", 0))

        return {
            "total_chunks": len(all_data["ids"]),
            "documents": sorted(sources),
            "years": sorted(years),
        }
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return {"total_chunks": 0, "documents": [], "years": [], "error": str(e)}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    count = ingest_documents()
    print(f"\nIngested {count} chunks from design documents")
