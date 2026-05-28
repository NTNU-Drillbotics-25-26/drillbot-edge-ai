"""Benchmark script for Drillbot RAG pipeline.

Run from project root:
    python -m scripts.benchmark --host http://10.22.60.223:8000
"""

import argparse
import time
import statistics
import requests
from dataclasses import dataclass


@dataclass
class BenchmarkResult:
    question: str
    total_ms: float
    retrieval_ms: float | None
    llm_ms: float | None
    answer_length: int
    chunks_used: int


TEST_QUESTIONS = [
    "What does stuck bit mean?",
    "How do I enable drives?",
    "What is the left joystick for?",
    "How do I start autonomous mode?",
    "What alarms can occur?",
    "How does vibration feedback work?",
    "What is WOB?",
    "How do I change RPM?",
]


def benchmark_single(host: str, question: str, timeout: int = 120) -> BenchmarkResult:
    """Benchmark a single question."""
    payload = {"question": question, "ui_context": {}}

    start = time.perf_counter()
    resp = requests.post(f"{host}/ask", json=payload, timeout=timeout)
    total_ms = (time.perf_counter() - start) * 1000

    resp.raise_for_status()
    data = resp.json()

    # Server-side timing if available
    retrieval_ms = data.get("timing", {}).get("retrieval_ms")
    llm_ms = data.get("timing", {}).get("llm_ms")

    return BenchmarkResult(
        question=question,
        total_ms=total_ms,
        retrieval_ms=retrieval_ms,
        llm_ms=llm_ms,
        answer_length=len(data.get("answer", "")),
        chunks_used=data.get("chunks_used", 0),
    )


def run_benchmark(host: str, questions: list[str], warmup: int = 1, runs: int = 3):
    """Run benchmark suite."""
    print(f"Benchmarking {host}")
    print(f"Warmup runs: {warmup}, Timed runs: {runs}")
    print("=" * 60)

    # Check health
    try:
        health = requests.get(f"{host}/health", timeout=5).json()
        print(f"Model: {health.get('model', 'unknown')}")
    except Exception as e:
        print(f"Warning: Health check failed: {e}")

    print()

    # Warmup
    if warmup > 0:
        print("Warming up...")
        for _ in range(warmup):
            try:
                benchmark_single(host, questions[0])
            except Exception as e:
                print(f"  Warmup error: {e}")
        print()

    # Timed runs
    all_results: list[BenchmarkResult] = []

    for q in questions:
        print(f"Q: {q[:50]}...")
        times = []

        for run in range(runs):
            try:
                result = benchmark_single(host, q)
                times.append(result.total_ms)

                if run == 0:
                    # Show server-side breakdown on first run
                    if result.retrieval_ms is not None:
                        print(f"  Retrieval: {result.retrieval_ms:.1f}ms")
                    if result.llm_ms is not None:
                        print(f"  LLM: {result.llm_ms:.1f}ms")
                    print(f"  Answer: {result.answer_length} chars, {result.chunks_used} chunks")

                all_results.append(result)
            except Exception as e:
                print(f"  Run {run+1} error: {e}")

        if times:
            avg = statistics.mean(times)
            std = statistics.stdev(times) if len(times) > 1 else 0
            print(f"  Total: {avg:.0f}ms (±{std:.0f}ms)")
        print()

    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)

    if all_results:
        totals = [r.total_ms for r in all_results]
        print(f"Total requests: {len(all_results)}")
        print(f"Avg response time: {statistics.mean(totals):.0f}ms")
        print(f"Min: {min(totals):.0f}ms, Max: {max(totals):.0f}ms")

        if all_results[0].retrieval_ms is not None:
            retrievals = [r.retrieval_ms for r in all_results if r.retrieval_ms]
            llms = [r.llm_ms for r in all_results if r.llm_ms]
            if retrievals:
                print(f"Avg retrieval: {statistics.mean(retrievals):.1f}ms")
            if llms:
                print(f"Avg LLM inference: {statistics.mean(llms):.0f}ms")


def main():
    parser = argparse.ArgumentParser(description="Benchmark Drillbot API")
    parser.add_argument("--host", default="http://localhost:8000", help="API host URL")
    parser.add_argument("--warmup", type=int, default=1, help="Warmup runs")
    parser.add_argument("--runs", type=int, default=3, help="Timed runs per question")
    parser.add_argument("--quick", action="store_true", help="Use fewer questions")
    args = parser.parse_args()

    questions = TEST_QUESTIONS[:3] if args.quick else TEST_QUESTIONS
    run_benchmark(args.host, questions, args.warmup, args.runs)


if __name__ == "__main__":
    main()
