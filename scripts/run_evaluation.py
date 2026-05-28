"""CLI entry point for running evaluations.

Usage:
    # Quick test (3 questions, local Ollama only)
    python -m scripts.run_evaluation --quick

    # Compare local Ollama vs OpenAI
    python -m scripts.run_evaluation --providers ollama_local openai

    # Test against actual Pi over network
    python -m scripts.run_evaluation --providers ollama_remote --pi-host 10.22.60.223

    # Full A/B comparison
    python -m scripts.run_evaluation --all --providers ollama_local openai
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from evaluation.providers import (
    OllamaLocalProvider,
    OllamaRemoteProvider,
    OpenAIProvider,
)
from evaluation.runner import EvaluationRunner
from evaluation.questions import get_question_set
from evaluation.config import OPENAI_API_KEY, PI_HOST


def create_providers(
    provider_names: list[str],
    pi_host: str | None = None,
    openai_key: str | None = None,
) -> list:
    """Create provider instances based on names."""
    providers = []

    for name in provider_names:
        if name == "ollama_local":
            providers.append(OllamaLocalProvider())
        elif name == "ollama_remote":
            host = pi_host or PI_HOST
            providers.append(OllamaRemoteProvider(host=host))
        elif name == "openai":
            key = openai_key or OPENAI_API_KEY
            providers.append(OpenAIProvider(api_key=key if key else None))
        else:
            print(f"Warning: Unknown provider '{name}', skipping.")

    return providers


def main():
    parser = argparse.ArgumentParser(
        description="Run RAG evaluation across LLM providers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m scripts.run_evaluation --quick
  python -m scripts.run_evaluation --providers ollama_local openai
  python -m scripts.run_evaluation --all --providers ollama_local openai
  python -m scripts.run_evaluation --providers ollama_remote --pi-host 10.22.60.223
        """,
    )

    parser.add_argument(
        "--quick",
        action="store_true",
        help="Quick test with 3 questions and local Ollama only",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all test questions (13 total)",
    )
    parser.add_argument(
        "--questions",
        choices=["quick", "basic", "edge", "complex", "all"],
        default="basic",
        help="Question set to use (default: basic)",
    )
    parser.add_argument(
        "--providers",
        nargs="+",
        choices=["ollama_local", "ollama_remote", "openai"],
        default=["ollama_local"],
        help="Providers to test (default: ollama_local)",
    )
    parser.add_argument(
        "--pi-host",
        help=f"Pi hostname/IP for ollama_remote (default: {PI_HOST})",
    )
    parser.add_argument(
        "--openai-key",
        help="OpenAI API key (or set OPENAI_API_KEY env var)",
    )
    parser.add_argument(
        "--mode",
        choices=["fts", "embed", "hybrid"],
        default="fts",
        help="Retrieval mode (default: fts)",
    )
    parser.add_argument(
        "--output-dir",
        default="evaluation/results",
        help="Output directory for results",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Only check provider availability, don't run evaluation",
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Minimal output",
    )

    args = parser.parse_args()

    # Handle --quick shortcut
    if args.quick:
        args.questions = "quick"
        args.providers = ["ollama_local"]

    # Handle --all shortcut
    if args.all:
        args.questions = "all"

    # Create providers
    providers = create_providers(
        args.providers,
        pi_host=args.pi_host,
        openai_key=args.openai_key,
    )

    if not providers:
        print("Error: No valid providers specified.")
        sys.exit(1)

    # Check availability
    print("Checking provider availability...")
    for p in providers:
        available = p.is_available()
        status = "[OK] available" if available else "[--] not available"
        print(f"  {p.name} ({p.model_name}): {status}")

    if args.check:
        sys.exit(0)

    # Filter to available providers
    available_providers = [p for p in providers if p.is_available()]
    if not available_providers:
        print("\nError: No providers are available. Check that Ollama is running.")
        sys.exit(1)

    # Get questions
    questions = get_question_set(args.questions)
    print(f"\nRunning {len(questions)} questions across {len(available_providers)} providers...")

    # Create runner (import RetrievalMode here to defer app loading)
    from app.hybrid import RetrievalMode
    retrieval_mode = RetrievalMode(args.mode)
    runner = EvaluationRunner(
        providers=available_providers,
        retrieval_mode=retrieval_mode,
        output_dir=args.output_dir,
    )

    # Run evaluation
    try:
        runner.run_questions(questions, verbose=not args.quiet)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")

    # Save results
    json_path, csv_path = runner.save_results()
    print(f"\n{'='*60}")
    print("Results saved:")
    print(f"  JSON: {json_path}")
    print(f"  CSV:  {csv_path}")
    print(f"\nView results with:")
    print(f"  python -m evaluation.viewer {json_path}")
    print(f"  python -m evaluation.viewer {json_path} --detail")


if __name__ == "__main__":
    main()
