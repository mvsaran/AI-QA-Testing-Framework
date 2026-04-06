from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any

from .config import Settings


def build_summary(
    settings: Settings,
    metrics: list[dict[str, Any]],
    test_outcomes: list[dict[str, Any]],
) -> dict[str, Any]:
    outcome_counter = Counter(item["outcome"] for item in test_outcomes)
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "settings": settings.public_dict(),
        "totals": {
            "tests": len(test_outcomes),
            "passed": outcome_counter.get("passed", 0),
            "failed": outcome_counter.get("failed", 0),
            "skipped": outcome_counter.get("skipped", 0),
        },
        "metrics": metrics,
        "test_outcomes": test_outcomes,
    }


def write_summary(report_file: Path, payload: dict[str, Any]) -> None:
    report_file.parent.mkdir(parents=True, exist_ok=True)
    with report_file.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)


def build_consolidated_summary(payload: dict[str, Any]) -> dict[str, Any]:
    metrics = payload.get("metrics", [])
    test_outcomes = payload.get("test_outcomes", [])

    metrics_by_name: dict[str, list[dict[str, Any]]] = {}
    metrics_by_case: dict[str, list[dict[str, Any]]] = {}
    for item in metrics:
        metrics_by_name.setdefault(str(item["metric"]), []).append(item)
        metrics_by_case.setdefault(str(item["case_id"]), []).append(item)

    metric_overview = []
    for metric_name, items in sorted(metrics_by_name.items()):
        scores = [float(item["score"]) for item in items]
        passed = sum(1 for item in items if item["outcome"] == "passed")
        failed = sum(1 for item in items if item["outcome"] == "failed")
        metric_overview.append(
            {
                "metric": metric_name,
                "count": len(items),
                "average_score": round(sum(scores) / len(scores), 4),
                "min_score": round(min(scores), 4),
                "max_score": round(max(scores), 4),
                "passed": passed,
                "failed": failed,
            }
        )

    question_overview = []
    for case_id, items in sorted(metrics_by_case.items()):
        question = str(items[0]["question"]) if items else case_id
        avg_score = round(sum(float(item["score"]) for item in items) / len(items), 4) if items else None
        question_overview.append(
            {
                "case_id": case_id,
                "question": question,
                "metrics": [
                    {
                        "metric": str(item["metric"]),
                        "score": float(item["score"]),
                        "threshold": float(item["threshold"]),
                        "outcome": str(item["outcome"]),
                    }
                    for item in items
                ],
                "average_score": avg_score,
                "overall_outcome": "failed" if any(item["outcome"] == "failed" for item in items) else "passed",
            }
        )

    slowest_tests = sorted(
        (
            {
                "nodeid": str(item["nodeid"]),
                "outcome": str(item["outcome"]),
                "duration_seconds": float(item["duration_seconds"]),
            }
            for item in test_outcomes
        ),
        key=lambda item: item["duration_seconds"],
        reverse=True,
    )[:5]

    failed_metrics = [item for item in metrics if item["outcome"] == "failed"]
    if payload["totals"]["failed"] > 0 or failed_metrics:
        verdict = "Blocked"
    elif payload["totals"]["skipped"] > 0:
        verdict = "Warning"
    else:
        verdict = "Ready"

    return {
        "generated_at_utc": payload["generated_at_utc"],
        "verdict": verdict,
        "totals": payload["totals"],
        "metric_overview": metric_overview,
        "question_overview": question_overview,
        "slowest_tests": slowest_tests,
        "raw_report_paths": {
            "summary_json": payload["settings"]["report_file"],
            "summary_html": payload["settings"]["html_report_file"],
        },
    }


def write_html_report(report_file: Path, payload: dict[str, Any]) -> None:
    report_file.parent.mkdir(parents=True, exist_ok=True)

    totals = payload["totals"]
    metrics_rows = "".join(
        (
            "<tr>"
            f"<td>{escape(str(item['metric']))}</td>"
            f"<td>{escape(str(item['case_id']))}</td>"
            f"<td>{escape(str(item['question']))}</td>"
            f"<td>{float(item['score']):.4f}</td>"
            f"<td>{float(item['threshold']):.4f}</td>"
            f"<td>{escape(str(item['outcome']))}</td>"
            "</tr>"
        )
        for item in payload["metrics"]
    )
    test_rows = "".join(
        (
            "<tr>"
            f"<td>{escape(str(item['nodeid']))}</td>"
            f"<td>{escape(str(item['outcome']))}</td>"
            f"<td>{float(item['duration_seconds']):.4f}</td>"
            "</tr>"
        )
        for item in payload["test_outcomes"]
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>AI QA Test Report</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; color: #1f2937; }}
    h1, h2 {{ margin-bottom: 8px; }}
    .summary {{ display: flex; gap: 16px; margin: 16px 0 24px; flex-wrap: wrap; }}
    .card {{ border: 1px solid #d1d5db; border-radius: 8px; padding: 12px 16px; min-width: 120px; }}
    table {{ border-collapse: collapse; width: 100%; margin: 12px 0 24px; }}
    th, td {{ border: 1px solid #d1d5db; padding: 8px; text-align: left; vertical-align: top; }}
    th {{ background: #f3f4f6; }}
    code {{ background: #f3f4f6; padding: 2px 4px; border-radius: 4px; }}
  </style>
</head>
<body>
  <h1>AI QA Test Report</h1>
  <p>Generated at <code>{escape(str(payload['generated_at_utc']))}</code></p>

  <div class="summary">
    <div class="card"><strong>Tests</strong><div>{totals['tests']}</div></div>
    <div class="card"><strong>Passed</strong><div>{totals['passed']}</div></div>
    <div class="card"><strong>Failed</strong><div>{totals['failed']}</div></div>
    <div class="card"><strong>Skipped</strong><div>{totals['skipped']}</div></div>
  </div>

  <h2>Metrics</h2>
  <table>
    <thead>
      <tr>
        <th>Metric</th>
        <th>Case ID</th>
        <th>Question</th>
        <th>Score</th>
        <th>Threshold</th>
        <th>Outcome</th>
      </tr>
    </thead>
    <tbody>{metrics_rows}</tbody>
  </table>

  <h2>Test Outcomes</h2>
  <table>
    <thead>
      <tr>
        <th>Test</th>
        <th>Outcome</th>
        <th>Duration Seconds</th>
      </tr>
    </thead>
    <tbody>{test_rows}</tbody>
  </table>
</body>
</html>
"""
    with report_file.open("w", encoding="utf-8") as handle:
        handle.write(html)


def write_consolidated_html_report(report_file: Path, payload: dict[str, Any]) -> None:
    report_file.parent.mkdir(parents=True, exist_ok=True)

    metric_rows = "".join(
        (
            "<tr>"
            f"<td>{escape(item['metric'])}</td>"
            f"<td>{item['count']}</td>"
            f"<td>{item['average_score']:.4f}</td>"
            f"<td>{item['min_score']:.4f}</td>"
            f"<td>{item['max_score']:.4f}</td>"
            f"<td>{item['passed']}</td>"
            f"<td>{item['failed']}</td>"
            "</tr>"
        )
        for item in payload["metric_overview"]
    )
    question_rows = "".join(
        (
            "<tr>"
            f"<td>{escape(item['case_id'])}</td>"
            f"<td>{escape(item['question'])}</td>"
            f"<td>{_format_optional_score(item['average_score'])}</td>"
            f"<td>{escape(item['overall_outcome'])}</td>"
            "</tr>"
        )
        for item in payload["question_overview"]
    )
    slow_rows = "".join(
        (
            "<tr>"
            f"<td>{escape(item['nodeid'])}</td>"
            f"<td>{escape(item['outcome'])}</td>"
            f"<td>{item['duration_seconds']:.4f}</td>"
            "</tr>"
        )
        for item in payload["slowest_tests"]
    )

    totals = payload["totals"]
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>AI QA Consolidated Report</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; color: #1f2937; }}
    h1, h2 {{ margin-bottom: 8px; }}
    .summary {{ display: flex; gap: 16px; margin: 16px 0 24px; flex-wrap: wrap; }}
    .card {{ border: 1px solid #d1d5db; border-radius: 8px; padding: 12px 16px; min-width: 120px; }}
    .verdict {{ font-size: 18px; font-weight: bold; }}
    table {{ border-collapse: collapse; width: 100%; margin: 12px 0 24px; }}
    th, td {{ border: 1px solid #d1d5db; padding: 8px; text-align: left; vertical-align: top; }}
    th {{ background: #f3f4f6; }}
    code {{ background: #f3f4f6; padding: 2px 4px; border-radius: 4px; }}
  </style>
</head>
<body>
  <h1>AI QA Consolidated Report</h1>
  <p>Generated at <code>{escape(str(payload['generated_at_utc']))}</code></p>
  <p class="verdict">Final Verdict: {escape(payload['verdict'])}</p>

  <div class="summary">
    <div class="card"><strong>Tests</strong><div>{totals['tests']}</div></div>
    <div class="card"><strong>Passed</strong><div>{totals['passed']}</div></div>
    <div class="card"><strong>Failed</strong><div>{totals['failed']}</div></div>
    <div class="card"><strong>Skipped</strong><div>{totals['skipped']}</div></div>
  </div>

  <h2>Metric Overview</h2>
  <table>
    <thead>
      <tr>
        <th>Metric</th><th>Count</th><th>Average</th><th>Min</th><th>Max</th><th>Passed</th><th>Failed</th>
      </tr>
    </thead>
    <tbody>{metric_rows}</tbody>
  </table>

  <h2>Question Overview</h2>
  <table>
    <thead>
      <tr>
        <th>Case ID</th><th>Question</th><th>Average Score</th><th>Outcome</th>
      </tr>
    </thead>
    <tbody>{question_rows}</tbody>
  </table>

  <h2>Slowest Tests</h2>
  <table>
    <thead>
      <tr>
        <th>Test</th><th>Outcome</th><th>Duration Seconds</th>
      </tr>
    </thead>
    <tbody>{slow_rows}</tbody>
  </table>
</body>
</html>
"""
    with report_file.open("w", encoding="utf-8") as handle:
        handle.write(html)


def _format_optional_score(score: Any) -> str:
    if score is None:
        return "n/a"
    return f"{float(score):.4f}"
