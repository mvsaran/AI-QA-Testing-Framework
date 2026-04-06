from __future__ import annotations

import sys
from pathlib import Path
from typing import Callable

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from aiqa_testing.client import build_embeddings, build_evaluator_llm, is_rag_api_available
from aiqa_testing.config import Settings, load_settings
from aiqa_testing.datasets import load_test_cases
from aiqa_testing.reporting import (
    build_consolidated_summary,
    build_summary,
    write_consolidated_html_report,
    write_html_report,
    write_summary,
)

def pytest_configure(config: pytest.Config) -> None:
    config._aiqa_metrics = []
    config._aiqa_outcomes = []


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    outcome = yield
    report = outcome.get_result()
    if report.when not in {"call", "setup"}:
        return
    if report.when == "setup" and report.outcome != "skipped":
        return
    if report.when == "call" and report.outcome == "skipped":
        return

    item.config._aiqa_outcomes.append(
        {
            "nodeid": report.nodeid,
            "outcome": report.outcome,
            "duration_seconds": round(report.duration, 4),
        }
    )


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    settings = load_settings()
    summary = build_summary(
        settings=settings,
        metrics=session.config._aiqa_metrics,
        test_outcomes=session.config._aiqa_outcomes,
    )
    consolidated = build_consolidated_summary(summary)
    write_summary(settings.report_file, summary)
    write_html_report(settings.html_report_file, summary)
    write_summary(settings.consolidated_report_file, consolidated)
    write_consolidated_html_report(settings.consolidated_html_report_file, consolidated)


@pytest.fixture(scope="session")
def settings() -> Settings:
    return load_settings()


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    if "test_case" in metafunc.fixturenames:
        settings = load_settings()
        cases = load_test_cases(settings.dataset_path)
        metafunc.parametrize("test_case", cases, ids=[case.case_id for case in cases])


@pytest.fixture(scope="session")
def evaluator_llm(settings: Settings):
    return build_evaluator_llm(settings)


@pytest.fixture(scope="session")
def embeddings(settings: Settings):
    return build_embeddings(settings)


@pytest.fixture(scope="session")
def require_rag_api(settings: Settings):
    if not is_rag_api_available(settings):
        pytest.skip(
            "RAG API is not reachable. Start the server or set RAG_API_BASE_URL to a running endpoint."
        )


@pytest.fixture
def record_metric(request: pytest.FixtureRequest) -> Callable[[str, object, float, float], None]:
    def _record(metric: str, test_case: object, score: float, threshold: float) -> None:
        request.config._aiqa_metrics.append(
            {
                "metric": metric,
                "case_id": getattr(test_case, "case_id", "unknown"),
                "question": getattr(test_case, "question", "unknown"),
                "score": score,
                "threshold": threshold,
                "outcome": "passed" if score >= threshold else "failed",
            }
        )

    return _record
