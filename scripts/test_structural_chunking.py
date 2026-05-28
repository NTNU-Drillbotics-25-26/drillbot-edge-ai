"""Test script to verify structural chunking is working correctly.

Usage:
    python -m scripts.test_structural_chunking
    python -m scripts.test_structural_chunking --file path/to/thesis.pdf
    python -m scripts.test_structural_chunking --sample  # Use sample text
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.ingest_docs import (
    STRUCT_CHUNK_MAX_WORDS,
    STRUCT_CHUNK_MIN_WORDS,
    chunk_pdf_structured,
    chunk_thesis_structured,
    extract_pdf_with_pages,
    extract_pdf_pages_clean,
    extract_text,
    parse_structure,
)

# Sample thesis-like text for testing
SAMPLE_TEXT = """
Chapter 1 Introduction

This thesis explores the development of autonomous drilling systems for the Drillbotics
competition. The work builds upon previous years' designs while introducing novel
control algorithms and sensor integration strategies.

1.1 Background

The petroleum industry has long sought to automate drilling operations to improve
safety and efficiency. Manual drilling operations require constant human oversight
and are prone to errors that can result in costly delays or equipment damage.

Recent advances in sensor technology and machine learning have opened new
possibilities for autonomous drilling control. This thesis investigates how these
technologies can be applied to small-scale drilling rigs.

1.2 Problem Statement

The main research question addressed in this thesis is: How can we design an
autonomous drilling control system that optimizes rate of penetration while
minimizing the risk of bit damage and borehole instability?

1.2.1 Sub-objectives

The following sub-objectives guide our research:

First, we aim to develop a real-time sensor fusion algorithm that combines
data from multiple sources including weight-on-bit sensors, rotational speed
encoders, and vibration monitors.

Second, we seek to implement a predictive control system that adjusts drilling
parameters based on predicted formation characteristics.

Chapter 2 Literature Review

This chapter reviews existing literature on autonomous drilling systems and
identifies gaps that this research aims to address.

2.1 Historical Context

Early attempts at drilling automation date back to the 1980s when programmable
logic controllers were first introduced to drilling operations. These systems
provided basic automation of discrete tasks but lacked the intelligence for
true autonomous operation.

2.2 Modern Approaches

Contemporary autonomous drilling systems leverage advances in artificial
intelligence and sensor technology. Key developments include the application
of neural networks for formation identification and model predictive control
for drilling parameter optimization.

Chapter 3 Methodology

This chapter describes the research methodology employed in this thesis,
including the experimental setup and data collection procedures.

3.1 Experimental Setup

The experiments were conducted using the NTNU Drillbotics test rig, which
features a scaled-down drilling assembly with comprehensive instrumentation.
The rig includes sensors for measuring weight-on-bit, rotational speed,
torque, and vibration across multiple axes.

3.2 Data Collection

Data was collected during drilling trials conducted over a six-month period.
Each trial involved drilling through standardized rock samples with varying
mechanical properties to evaluate system performance under different conditions.
"""


def test_structure_parsing(text: str) -> None:
    """Test and display the parsed document structure."""
    print("\n" + "=" * 60)
    print("STRUCTURE PARSING TEST")
    print("=" * 60)

    root = parse_structure(text)

    def print_tree(node, indent=0):
        prefix = "  " * indent
        level_names = {0: "ROOT", 1: "CHAPTER", 2: "SECTION", 3: "SUBSECTION", 4: "PARA"}
        level_name = level_names.get(node.level, f"L{node.level}")
        words = node.word_count()
        content_preview = node.content[:50] + "..." if len(node.content) > 50 else node.content
        content_preview = content_preview.replace("\n", " ")

        print(f"{prefix}[{level_name}] {node.title or '(untitled)'} ({words} words)")
        if node.content and indent < 3:  # Show content preview for top levels
            print(f"{prefix}  Content: \"{content_preview}\"")

        for child in node.children:
            print_tree(child, indent + 1)

    print_tree(root)


def test_chunking(text: str, max_words: int | None = None) -> None:
    """Test and display the chunking results."""
    # Use smaller limit for demo if text is small
    total_words = len(text.split())
    if max_words is None:
        max_words = min(STRUCT_CHUNK_MAX_WORDS, total_words // 3) if total_words < 500 else STRUCT_CHUNK_MAX_WORDS
    min_words = max(20, max_words // 8)

    print("\n" + "=" * 60)
    print("STRUCTURAL CHUNKING TEST")
    print(f"Settings: max_words={max_words}, min_words={min_words}")
    print(f"Total document words: {total_words}")
    print("=" * 60)

    # Import the chunking function components to use custom limits
    from app.ingest_docs import clean_citations, parse_structure, chunk_structural

    text_clean = clean_citations(text)
    root = parse_structure(text_clean)
    chunks = list(chunk_structural(root, max_words=max_words, min_words=min_words))

    print(f"\nGenerated {len(chunks)} chunks:\n")

    for i, chunk_data in enumerate(chunks):
        chunk_text = chunk_data["text"]
        metadata = {
            "heading_path": chunk_data["heading_path"],
            "structural_level": chunk_data["level"],
            "section_title": chunk_data["title"],
        }
        word_count = len(chunk_text.split())
        preview = chunk_text[:100].replace("\n", " ") + "..." if len(chunk_text) > 100 else chunk_text.replace("\n", " ")

        print(f"Chunk {i + 1}:")
        print(f"  Path: {metadata.get('heading_path', 'N/A')}")
        print(f"  Level: {metadata.get('structural_level', 'N/A')}")
        print(f"  Section: {metadata.get('section_title', 'N/A')}")
        print(f"  Words: {word_count}")
        print(f"  Preview: \"{preview}\"")
        print()


def test_pdf_file(path: Path, max_words: int | None = None) -> None:
    """Test structural chunking on a real PDF file."""
    print("\n" + "=" * 60)
    print(f"PDF STRUCTURAL CHUNKING: {path.name}")
    print("=" * 60)

    # Use cleaned extraction (removes page headers/footers/numbers)
    pages = extract_pdf_pages_clean(path)
    print(f"Extracted and cleaned {len(pages)} pages")

    if max_words:
        min_words = max(20, max_words // 8)
        chunks = chunk_pdf_structured(pages, max_words=max_words, min_words=min_words)
    else:
        chunks = chunk_pdf_structured(pages)
    print(f"Generated {len(chunks)} structural chunks\n")

    # Show summary by section
    sections = {}
    for chunk_text, metadata, page_start, page_end in chunks:
        path_key = metadata.get("heading_path", "Unknown")
        if path_key not in sections:
            sections[path_key] = {"count": 0, "words": 0, "pages": set()}
        sections[path_key]["count"] += 1
        sections[path_key]["words"] += len(chunk_text.split())
        sections[path_key]["pages"].add(page_start)
        if page_end:
            sections[path_key]["pages"].add(page_end)

    print("Chunks by section:")
    print("-" * 60)
    for section, stats in sorted(sections.items()):
        pages_str = f"pp. {min(stats['pages'])}-{max(stats['pages'])}" if stats['pages'] else ""
        section_clean = section.encode('ascii', 'replace').decode('ascii')
        print(f"  {section_clean}")
        print(f"    {stats['count']} chunks, {stats['words']} words, {pages_str}")
    print()

    # Show first few chunks in detail
    print("\nFirst 5 chunks in detail:")
    print("-" * 60)
    for i, (chunk_text, metadata, page_start, page_end) in enumerate(chunks[:5]):
        word_count = len(chunk_text.split())
        # Clean preview for terminal display (replace problematic chars)
        preview = chunk_text[:150].replace("\n", " ")
        preview = preview.encode('ascii', 'replace').decode('ascii') + "..."

        print(f"\nChunk {i + 1}:")
        print(f"  Section: {metadata.get('heading_path', 'N/A')}")
        print(f"  Pages: {page_start}-{page_end}")
        print(f"  Words: {word_count}")
        print(f"  Preview: \"{preview}\"")


def show_detected_headings(path: Path) -> None:
    """Show all headings detected in a PDF to debug detection."""
    from app.ingest_docs import extract_pdf_pages_clean, _detect_heading

    print("\n" + "=" * 60)
    print(f"HEADING DETECTION DEBUG: {path.name}")
    print("=" * 60)

    pages = extract_pdf_pages_clean(path)
    full_text = "\n\n".join(text for text, _ in pages)

    detected = []
    for line in full_text.split('\n'):
        line = line.strip()
        if not line:
            continue
        heading = _detect_heading(line)
        if heading:
            level, title = heading
            detected.append((level, title, line[:60]))

    print(f"\nDetected {len(detected)} headings:\n")
    for level, title, raw in detected:
        level_names = {1: "CHAP", 2: "SECT", 3: "SUB", 4: "SUBSUB"}
        print(f"  [{level_names.get(level, f'L{level}')}] {title}")

    # Also show potential headings that were rejected (for debugging)
    print("\n" + "-" * 60)
    print("Potential headings (numbered lines that weren't detected):")
    print("-" * 60)

    numbered_pattern = re.compile(r'^(\d+\.?\d*\.?\d*)\s+(.+)$')
    shown = 0
    for line in full_text.split('\n'):
        line = line.strip()
        if not line or len(line) > 80:
            continue
        match = numbered_pattern.match(line)
        if match and not _detect_heading(line):
            if shown < 30:  # Limit output
                print(f"  REJECTED: {line[:70].encode('ascii', 'replace').decode('ascii')}")
                shown += 1

    print()


def main():
    parser = argparse.ArgumentParser(description="Test structural chunking")
    parser.add_argument("--file", "-f", type=Path, help="Path to PDF or text file to test")
    parser.add_argument("--sample", "-s", action="store_true", help="Use sample thesis text")
    parser.add_argument("--max-words", "-m", type=int, default=None, help="Max words per chunk (default: auto)")
    parser.add_argument("--debug-headings", "-d", action="store_true", help="Show detected headings only")
    args = parser.parse_args()

    if args.file:
        if not args.file.exists():
            print(f"Error: File not found: {args.file}")
            sys.exit(1)

        # Debug mode - just show headings
        if args.debug_headings:
            if args.file.suffix.lower() == ".pdf":
                show_detected_headings(args.file)
            else:
                print("Debug headings mode only works with PDF files")
            return

        if args.file.suffix.lower() == ".pdf":
            test_pdf_file(args.file, max_words=args.max_words)
        else:
            text = extract_text(args.file)
            if text:
                test_structure_parsing(text)
                test_chunking(text, max_words=args.max_words)
            else:
                print(f"Error: Could not extract text from {args.file}")
                sys.exit(1)
    else:
        # Use sample text
        print("Using sample thesis text for testing...")
        test_structure_parsing(SAMPLE_TEXT)
        test_chunking(SAMPLE_TEXT, max_words=args.max_words)

    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
