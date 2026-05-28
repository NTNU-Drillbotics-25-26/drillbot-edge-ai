"""CLI script for ingesting design documents into the vector store.

Usage:
    python -m scripts.ingest_documents [--dir PATH] [--stats]

Examples:
    # Ingest from default documents/ directory
    python -m scripts.ingest_documents

    # Ingest from a specific directory
    python -m scripts.ingest_documents --dir /path/to/docs

    # Show current document statistics
    python -m scripts.ingest_documents --stats
"""

import argparse
import logging
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.ingest_docs import (
    DOCUMENTS_DIR,
    ingest_documents,
    get_document_stats,
    iter_documents,
)


def main():
    parser = argparse.ArgumentParser(
        description="Ingest design documents into vector store",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m scripts.ingest_documents              # Ingest all documents
  python -m scripts.ingest_documents --stats      # Show statistics
  python -m scripts.ingest_documents --list       # List documents to ingest
  python -m scripts.ingest_documents --dir ./my_docs  # Custom directory
        """,
    )
    parser.add_argument(
        "--dir",
        type=Path,
        default=DOCUMENTS_DIR,
        help=f"Directory containing documents (default: {DOCUMENTS_DIR})",
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show statistics about indexed documents",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List documents that would be ingested",
    )
    parser.add_argument(
        "--keep-existing",
        action="store_true",
        help="Don't clear existing embeddings before ingesting",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output",
    )

    args = parser.parse_args()

    # Configure logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(levelname)s: %(message)s",
    )

    # Show stats
    if args.stats:
        stats = get_document_stats()
        print("\n=== Document Index Statistics ===")
        print(f"Total chunks indexed: {stats['total_chunks']}")
        print(f"Documents: {len(stats['documents'])}")
        for doc in stats["documents"]:
            print(f"  - {doc}")
        print(f"Years covered: {stats['years']}")
        if "error" in stats:
            print(f"Error: {stats['error']}")
        return

    # List documents
    if args.list:
        docs_dir = args.dir
        print(f"\n=== Documents in {docs_dir} ===")
        docs = list(iter_documents(docs_dir))
        if not docs:
            print("No supported documents found.")
            print("Supported formats: .pdf, .docx, .txt, .md")
        else:
            for doc in docs:
                rel_path = doc.relative_to(docs_dir) if docs_dir in doc.parents else doc.name
                print(f"  {rel_path}")
            print(f"\nTotal: {len(docs)} documents")
        return

    # Ingest documents
    docs_dir = args.dir
    if not docs_dir.exists():
        print(f"Creating documents directory: {docs_dir}")
        docs_dir.mkdir(parents=True, exist_ok=True)
        print("\nDirectory structure for documents:")
        print("  documents/")
        print("  ├── 2024/")
        print("  │   └── design_report_2024.pdf")
        print("  ├── 2025/")
        print("  │   └── design_report_2025.pdf")
        print("  └── 2026/")
        print("      └── current_spec.docx")
        print("\nAdd your documents and run this script again.")
        return

    docs = list(iter_documents(docs_dir))
    if not docs:
        print(f"No documents found in {docs_dir}")
        print("Supported formats: .pdf, .docx, .txt, .md")
        print("\nOrganize documents by year:")
        print("  documents/2024/report.pdf")
        print("  documents/2025/report.pdf")
        return

    print(f"\n=== Ingesting {len(docs)} documents from {docs_dir} ===\n")

    count = ingest_documents(
        docs_dir=docs_dir,
        clear_existing=not args.keep_existing,
    )

    print(f"\n=== Ingestion Complete ===")
    print(f"Indexed {count} chunks from {len(docs)} documents")

    # Show updated stats
    stats = get_document_stats()
    print(f"Years covered: {stats['years']}")


if __name__ == "__main__":
    main()
