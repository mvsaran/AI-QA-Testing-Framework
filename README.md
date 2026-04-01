# AI QA Testing Framework

This is a standalone `pytest` project for evaluating a RAG API.

In simple terms, this project asks your AI application a set of benchmark questions, checks the answer and retrieved documents, and scores the result using `ragas`. It is meant to act like a quality gate for a Retrieval-Augmented Generation system.

## What The Project Does

The framework checks whether your RAG system:

- returns a valid API response
- gives a non-empty answer
- retrieves supporting context
- answers the user’s question directly
- stays grounded in the retrieved context
- avoids missing important supporting context
- stays within a reasonable latency budget

## How It Works

1. Test cases are loaded from `datasets/test_cases.json`.
2. The framework sends each question to `POST /ask` on your RAG API.
3. The response is parsed into typed Python models.
4. Retrieved document text is extracted from `documents[*].page_content`.
5. `ragas` metrics evaluate the answer quality.
6. Thresholds from environment variables decide pass or fail.
7. A JSON summary report is written to `reports/latest-summary.json`.

## Project Structure

```text
AIQATestingFramework/
|-- .env.example
|-- .gitignore
|-- pyproject.toml
|-- pytest.ini
|-- README.md
|-- __init__.py
|-- datasets/
|   `-- test_cases.json
|-- reports/
|   `-- latest-summary.json
|-- src/
|   `-- aiqa_testing/
|       |-- __init__.py
|       |-- client.py
|       |-- config.py
|       |-- datasets.py
|       |-- models.py
|       |-- reporting.py
|       `-- sample_builder.py
|-- tests/
|   |-- __init__.py
|   |-- conftest.py
|   |-- test_answer_relevancy.py
|   |-- test_api_contract.py
|   |-- test_context_precision.py
|   |-- test_context_recall.py
|   |-- test_data.py
|   |-- test_faithfulness.py
|   |-- test_negative_cases.py
|   |-- test_regression_baseline.py
|   `-- test_smoke.py
`-- .github/
    `-- workflows/
        `-- qa.yml
```

## File-By-File Explanation

### Root Files

#### `.env.example`

Template file for the environment variables required by the framework.

Purpose:

- shows what values must be configured
- documents models, thresholds, timeouts, and report paths

#### `.gitignore`

Prevents local-only and generated files from being committed.

Purpose:

- ignores `.env`
- ignores virtual environments and caches
- ignores generated reports

#### `pyproject.toml`

Defines the standalone project metadata and dependencies.

Purpose:

- makes the framework installable with `pip install -e .`
- defines the build system
- registers package discovery under `src/`

#### `pytest.ini`

Pytest configuration for this project.

Purpose:

- enables async pytest mode
- limits test discovery to the `tests/` folder
- registers custom markers like `regression`, `smoke`, `contract`, and `negative`

#### `README.md`

Project documentation.

Purpose:

- explains the framework in plain language
- documents the structure, files, and run commands

#### `__init__.py`

Package marker at the project root.

Purpose:

- prevents module-name collisions when tests are collected from the repository root

### Dataset

#### `datasets/test_cases.json`

The benchmark dataset used by regression tests.

Purpose:

- stores the list of questions and reference answers outside the code
- makes it easy to add or edit evaluation coverage without changing test logic

### Source Code

#### `src/aiqa_testing/__init__.py`

Exports the main configuration objects.

Purpose:

- provides a simple entry point for package imports

#### `src/aiqa_testing/config.py`

Loads all runtime settings from environment variables.

Purpose:

- centralizes configuration
- keeps defaults in one place
- controls thresholds, timeout values, dataset location, and report location

#### `src/aiqa_testing/models.py`

Defines typed models for API responses and test cases.

Purpose:

- validates the structure of the `/ask` response
- provides strong error messages for malformed payloads
- keeps test data structured and predictable

#### `src/aiqa_testing/datasets.py`

Loads the JSON dataset file into typed `TestCase` objects.

Purpose:

- separates dataset loading from test logic
- keeps test fixtures clean

#### `src/aiqa_testing/client.py`

Contains the API client and evaluator setup.

Purpose:

- calls the RAG API
- measures latency
- applies retry logic for unstable responses
- builds the evaluator LLM and embeddings used by `ragas`

#### `src/aiqa_testing/sample_builder.py`

Transforms API responses into `ragas`-ready objects.

Purpose:

- extracts retrieved contexts
- builds `SingleTurnSample`
- keeps metric tests concise

#### `src/aiqa_testing/reporting.py`

Builds and writes the JSON summary report.

Purpose:

- captures metric results and test outcomes
- supports CI and historical comparisons

### Tests

#### `tests/__init__.py`

Package marker for the tests folder.

Purpose:

- avoids test-module import collisions with other projects in the same repository

#### `tests/conftest.py`

Shared pytest fixtures and test-session hooks.

Purpose:

- loads settings
- generates test cases dynamically from the dataset
- creates evaluator fixtures
- records metric results and test outcomes
- writes the JSON report at the end of the run

#### `tests/test_data.py`

Validates the dataset itself.

Purpose:

- checks that the dataset is not empty
- checks that case IDs are unique

#### `tests/test_regression_baseline.py`

Baseline regression test for real API responses.

Purpose:

- verifies that every benchmark question returns a usable answer
- verifies that retrieved contexts are present
- acts as a simple regression safety net before metric-level scoring

#### `tests/test_context_precision.py`

Regression metric test for retrieval quality.

Purpose:

- checks whether the retrieved context is relevant enough to support the answer

#### `tests/test_faithfulness.py`

Regression metric test for grounding quality.

Purpose:

- checks whether the answer is supported by retrieved context rather than made up

#### `tests/test_answer_relevancy.py`

Regression metric test for question-answer fit.

Purpose:

- checks whether the answer actually addresses the user’s question

#### `tests/test_context_recall.py`

Regression metric test for retrieval coverage.

Purpose:

- checks whether the retrieval step missed important context needed for the answer

#### `tests/test_api_contract.py`

Contract tests for the response shape.

Purpose:

- verifies valid payload parsing
- checks the live API response structure
- ensures malformed payloads fail clearly

#### `tests/test_negative_cases.py`

Negative validation tests.

Purpose:

- checks that empty answers and bad documents are rejected
- simulates obviously bad or irrelevant responses

#### `tests/test_smoke.py`

Fast operational checks.

Purpose:

- checks API reachability
- checks latency against the configured budget

### CI

#### `.github/workflows/qa.yml`

GitHub Actions workflow for automated execution.

Purpose:

- installs the project
- runs the full suite
- generates report artifacts in CI

### Reports

#### `reports/latest-summary.json`

Generated output file from the test session.

Purpose:

- stores aggregate test counts
- stores metric values
- provides a machine-readable run summary

## Test Categories

### Regression Tests

These are the main quality tests for the live RAG system:

- `test_regression_baseline.py`
- `test_context_precision.py`
- `test_faithfulness.py`
- `test_answer_relevancy.py`
- `test_context_recall.py`

Run only regression tests:

```powershell
pytest -m regression
```

### Contract Tests

These validate API structure and parsing behavior.

```powershell
pytest -m contract
```

### Negative Tests

These confirm that malformed inputs or weak responses are detected properly.

```powershell
pytest -m negative
```

### Smoke Tests

These are quick checks for API availability and latency.

```powershell
pytest -m smoke
```

## Running The Project

```powershell
cd C:\Users\mvsar\PycharmProjects\LLMEvaluation\AIQATestingFramework
python -m venv .venv
.venv\Scripts\activate
pip install -e .
pytest
```

Run a single test file:

```powershell
pytest tests\test_regression_baseline.py
pytest tests\test_context_precision.py
pytest tests\test_smoke.py
```

Generate HTML and JUnit reports:

```powershell
pytest --html reports\report.html --self-contained-html --junitxml reports\junit.xml
```

## Environment Variables

```env
OPENAI_API_KEY=your_key_here
RAG_API_BASE_URL=http://localhost:8000
RAG_TOP_K=3
RAG_TIMEOUT_SECONDS=30
EVALUATOR_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small
THRESHOLD_CONTEXT_PRECISION=0.70
THRESHOLD_FAITHFULNESS=0.70
THRESHOLD_ANSWER_RELEVANCY=0.70
THRESHOLD_CONTEXT_RECALL=0.70
SMOKE_MAX_LATENCY_MS=8000
AIQA_REPORT_FILE=reports/latest-summary.json
AIQA_DATASET_PATH=datasets/test_cases.json
```

## Summary

`AIQATestingFramework` is a standalone quality-checking project for a RAG API.

It separates dataset loading, API calls, typed validation, metric scoring, reporting, and CI into clear modules. It now includes an explicit regression baseline test in addition to the metric-based regression suite.
