"""CLI viewer for evaluation results."""

import argparse
import sys
from pathlib import Path
from .recorder import Recorder, EvaluationRecord


def format_record_summary(record: EvaluationRecord) -> str:
    """Format a single record as a summary line."""
    status = "OK" if not record.llm.error else "ERR"
    return (
        f"[{record.id}] {status} | "
        f"{record.llm.provider:12} | "
        f"{record.total_ms:6.0f}ms | "
        f"{record.question[:40]}..."
    )


def format_record_detail(record: EvaluationRecord) -> str:
    """Format a single record with full details."""
    chunks_info = "\n".join(
        f"    - {c.get('title', 'untitled')} (score: {c.get('score', 0):.2f})"
        for c in record.retrieval.chunks
    )
    if not chunks_info:
        chunks_info = "    (no chunks retrieved)"

    return f"""
{'='*70}
ID: {record.id}
Timestamp: {record.timestamp}
Question: {record.question}

RETRIEVAL ({record.retrieval.mode}):
  Time: {record.retrieval.retrieval_ms:.1f}ms
  Chunks:
{chunks_info}

LLM ({record.llm.provider} / {record.llm.model_name}):
  Inference: {record.llm.inference_ms:.0f}ms
  Tokens: {record.llm.tokens_used or 'N/A'}
  Error: {record.llm.error or 'None'}

RESPONSE:
{record.llm.response}

TOTAL: {record.total_ms:.0f}ms | Grade: {record.grade or 'ungraded'}
{'='*70}
"""


def print_summary(records: list[EvaluationRecord]) -> None:
    """Print summary statistics."""
    if not records:
        print("No records to summarize.")
        return

    providers = {}
    for r in records:
        if r.llm.provider not in providers:
            providers[r.llm.provider] = {"times": [], "errors": 0}
        if r.llm.error:
            providers[r.llm.provider]["errors"] += 1
        else:
            providers[r.llm.provider]["times"].append(r.total_ms)

    print("\n" + "="*50)
    print("SUMMARY")
    print("="*50)
    print(f"Total evaluations: {len(records)}")
    print(f"Unique questions: {len(set(r.question for r in records))}")
    print()

    for provider, stats in providers.items():
        times = stats["times"]
        if times:
            avg = sum(times) / len(times)
            print(f"{provider}:")
            print(f"  Success: {len(times)}, Errors: {stats['errors']}")
            print(f"  Avg time: {avg:.0f}ms")
            print(f"  Range: {min(times):.0f}ms - {max(times):.0f}ms")
        else:
            print(f"{provider}:")
            print(f"  All failed ({stats['errors']} errors)")
        print()


def view_results(
    filepath: str,
    detail: bool = False,
    provider_filter: str | None = None,
    question_filter: str | None = None,
) -> None:
    """View results from a JSON file."""
    records = Recorder.load_json(filepath)

    if provider_filter:
        records = [r for r in records if provider_filter.lower() in r.llm.provider.lower()]

    if question_filter:
        records = [r for r in records if question_filter.lower() in r.question.lower()]

    if not records:
        print("No matching records found.")
        return

    if detail:
        for record in records:
            print(format_record_detail(record))
    else:
        print(f"\nResults from: {filepath}")
        print("-" * 70)
        for record in records:
            print(format_record_summary(record))

    print_summary(records)


def main():
    parser = argparse.ArgumentParser(description="View evaluation results")
    parser.add_argument("file", help="JSON results file to view")
    parser.add_argument("--detail", "-d", action="store_true", help="Show full details")
    parser.add_argument("--provider", "-p", help="Filter by provider name")
    parser.add_argument("--question", "-q", help="Filter by question text")

    args = parser.parse_args()

    if not Path(args.file).exists():
        print(f"Error: File not found: {args.file}")
        sys.exit(1)

    view_results(
        args.file,
        detail=args.detail,
        provider_filter=args.provider,
        question_filter=args.question,
    )


if __name__ == "__main__":
    main()
