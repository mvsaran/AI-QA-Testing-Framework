from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
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
