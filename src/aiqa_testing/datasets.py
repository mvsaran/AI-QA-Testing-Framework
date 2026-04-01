from __future__ import annotations

import json
from pathlib import Path

from .models import TestCase


def load_test_cases(dataset_path: Path) -> list[TestCase]:
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset file not found: {dataset_path}")

    with dataset_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    if not isinstance(payload, list) or not payload:
        raise ValueError("Dataset must be a non-empty JSON array.")

    return [TestCase.from_dict(item) for item in payload]
