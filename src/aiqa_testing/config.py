from __future__ import annotations

import os
from dataclasses import asdict, dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    project_root: Path
    dataset_path: Path
    report_file: Path
    html_report_file: Path
    consolidated_report_file: Path
    consolidated_html_report_file: Path
    rag_api_base_url: str
    rag_top_k: int
    rag_timeout_seconds: int
    evaluator_model: str
    embedding_model: str
    threshold_context_precision: float
    threshold_faithfulness: float
    threshold_answer_relevancy: float
    threshold_context_recall: float
    smoke_max_latency_ms: int

    def public_dict(self) -> dict[str, object]:
        data = asdict(self)
        data["project_root"] = str(self.project_root)
        data["dataset_path"] = str(self.dataset_path)
        data["report_file"] = str(self.report_file)
        data["html_report_file"] = str(self.html_report_file)
        data["consolidated_report_file"] = str(self.consolidated_report_file)
        data["consolidated_html_report_file"] = str(self.consolidated_html_report_file)
        return data


@lru_cache(maxsize=1)
def load_settings() -> Settings:
    project_root = Path(__file__).resolve().parents[2]
    dataset_path = project_root / os.getenv("AIQA_DATASET_PATH", "datasets/test_cases.json")
    report_file = project_root / os.getenv("AIQA_REPORT_FILE", "reports/latest-summary.json")
    html_report_file = project_root / os.getenv("AIQA_HTML_REPORT_FILE", "reports/report.html")
    consolidated_report_file = project_root / os.getenv(
        "AIQA_CONSOLIDATED_REPORT_FILE", "reports/consolidated-summary.json"
    )
    consolidated_html_report_file = project_root / os.getenv(
        "AIQA_CONSOLIDATED_HTML_REPORT_FILE", "reports/consolidated-report.html"
    )

    return Settings(
        project_root=project_root,
        dataset_path=dataset_path,
        report_file=report_file,
        html_report_file=html_report_file,
        consolidated_report_file=consolidated_report_file,
        consolidated_html_report_file=consolidated_html_report_file,
        rag_api_base_url=os.getenv("RAG_API_BASE_URL", "http://localhost:8000"),
        rag_top_k=int(os.getenv("RAG_TOP_K", "3")),
        rag_timeout_seconds=int(os.getenv("RAG_TIMEOUT_SECONDS", "30")),
        evaluator_model=os.getenv("EVALUATOR_MODEL", "gpt-4o-mini"),
        embedding_model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"),
        threshold_context_precision=float(os.getenv("THRESHOLD_CONTEXT_PRECISION", "0.70")),
        threshold_faithfulness=float(os.getenv("THRESHOLD_FAITHFULNESS", "0.70")),
        threshold_answer_relevancy=float(os.getenv("THRESHOLD_ANSWER_RELEVANCY", "0.70")),
        threshold_context_recall=float(os.getenv("THRESHOLD_CONTEXT_RECALL", "0.70")),
        smoke_max_latency_ms=int(os.getenv("SMOKE_MAX_LATENCY_MS", "8000")),
    )
