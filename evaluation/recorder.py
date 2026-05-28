"""Recording evaluation results to JSON and CSV."""

import json
import csv
import uuid
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Any


@dataclass
class RetrievalRecord:
    """Record of retrieval step."""

    mode: str
    retrieval_ms: float
    chunks: list[dict[str, Any]]


@dataclass
class LLMRecord:
    """Record of LLM response."""

    provider: str
    model_name: str
    prompt: str
    response: str
    inference_ms: float
    tokens_used: int | None = None
    error: str | None = None


@dataclass
class EvaluationRecord:
    """Complete record of one evaluation run."""

    id: str
    timestamp: str
    question: str
    retrieval: RetrievalRecord
    llm: LLMRecord
    total_ms: float
    grade: str | None = None  # For manual annotation: "good", "bad", "partial"
    notes: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "EvaluationRecord":
        data["retrieval"] = RetrievalRecord(**data["retrieval"])
        data["llm"] = LLMRecord(**data["llm"])
        return cls(**data)


class Recorder:
    """Records evaluation results to files."""

    def __init__(self, output_dir: str | Path = "evaluation/results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.records: list[EvaluationRecord] = []

    def record(
        self,
        question: str,
        retrieval_mode: str,
        retrieval_ms: float,
        chunks: list[dict],
        provider: str,
        model_name: str,
        prompt: str,
        response: str,
        inference_ms: float,
        tokens_used: int | None = None,
        error: str | None = None,
    ) -> EvaluationRecord:
        """Record a single evaluation result."""
        record = EvaluationRecord(
            id=str(uuid.uuid4())[:8],
            timestamp=datetime.now().isoformat(),
            question=question,
            retrieval=RetrievalRecord(
                mode=retrieval_mode,
                retrieval_ms=retrieval_ms,
                chunks=chunks,
            ),
            llm=LLMRecord(
                provider=provider,
                model_name=model_name,
                prompt=prompt,
                response=response,
                inference_ms=inference_ms,
                tokens_used=tokens_used,
                error=error,
            ),
            total_ms=retrieval_ms + inference_ms,
        )
        self.records.append(record)
        return record

    def save_json(self, filename: str | None = None) -> Path:
        """Save all records to a JSON file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"eval_{timestamp}.json"

        filepath = self.output_dir / filename
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(
                [r.to_dict() for r in self.records],
                f,
                indent=2,
                ensure_ascii=False,
            )
        return filepath

    def save_csv(self, filename: str | None = None) -> Path:
        """Save summary to CSV for spreadsheet analysis."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"eval_{timestamp}.csv"

        filepath = self.output_dir / filename
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "id",
                "timestamp",
                "question",
                "provider",
                "model",
                "retrieval_mode",
                "retrieval_ms",
                "inference_ms",
                "total_ms",
                "chunks_count",
                "response_preview",
                "error",
                "grade",
            ])
            for r in self.records:
                preview = r.llm.response[:100] + "..." if len(r.llm.response) > 100 else r.llm.response
                writer.writerow([
                    r.id,
                    r.timestamp,
                    r.question,
                    r.llm.provider,
                    r.llm.model_name,
                    r.retrieval.mode,
                    f"{r.retrieval.retrieval_ms:.1f}",
                    f"{r.llm.inference_ms:.1f}",
                    f"{r.total_ms:.1f}",
                    len(r.retrieval.chunks),
                    preview.replace("\n", " "),
                    r.llm.error or "",
                    r.grade or "",
                ])
        return filepath

    def save_all(self) -> tuple[Path, Path]:
        """Save both JSON and CSV files."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_path = self.save_json(f"eval_{timestamp}.json")
        csv_path = self.save_csv(f"eval_{timestamp}.csv")
        return json_path, csv_path

    @classmethod
    def load_json(cls, filepath: str | Path) -> list[EvaluationRecord]:
        """Load records from a JSON file."""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [EvaluationRecord.from_dict(d) for d in data]
