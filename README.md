# 🤖 AI QA Testing Framework

> **A production-grade `pytest` quality gate for Retrieval-Augmented Generation systems.**
> Ask your AI benchmark questions, score the answers with `ragas`, and enforce pass/fail thresholds — all in one automated pipeline.

---

## ✅ What The Framework Checks

| # | Check | Description |
|---|-------|-------------|
| 1 | 🔌 **API Response** | Returns a valid, parseable response |
| 2 | 💬 **Non-empty Answer** | Answer field is not blank or null |
| 3 | 📄 **Context Retrieved** | Supporting documents are present |
| 4 | 🎯 **Answer Relevancy** | Answer directly addresses the question |
| 5 | ⚓ **Faithfulness** | Answer is grounded in retrieved context |
| 6 | 🔍 **Context Recall** | No important supporting context is missing |
| 7 | ⚡ **Latency Budget** | Response time stays within configured limits |

---

## ⚙️ How It Works

```
📂 datasets/test_cases.json
        │
        ▼
🌐 POST /ask  ──►  RAG API
        │
        ▼
🧩 Parse into typed Python models
        │
        ▼
📊 Score with ragas metrics
        │
        ▼
🚦 Apply pass/fail thresholds
        │
        ▼
📝 Write reports/latest-summary.json
```

---

## 🗂️ Project Structure

```text
AIQATestingFramework/
├── 📄 .env.example                     ← Environment variable template
├── 🚫 .gitignore                       ← Excludes .env, venvs, reports
├── 📦 pyproject.toml                   ← Package metadata & dependencies
├── ⚙️  pytest.ini                      ← Async mode, markers, test discovery
├── 📖 README.md                        ← This file
├── 🗃️  datasets/
│   └── test_cases.json                 ← Benchmark questions & reference answers
├── 📊 reports/
│   └── latest-summary.json            ← Generated run summary
├── 🧠 src/
│   └── aiqa_testing/
│       ├── client.py                   ← API caller, retry logic, evaluator setup
│       ├── config.py                   ← Centralised env-var settings
│       ├── datasets.py                 ← JSON → typed TestCase loader
│       ├── models.py                   ← Typed API response models
│       ├── reporting.py                ← JSON report builder
│       └── sample_builder.py          ← ragas SingleTurnSample builder
├── 🧪 tests/
│   ├── conftest.py                     ← Fixtures, hooks, session report writer
│   ├── test_data.py                    ← Dataset integrity checks
│   ├── test_smoke.py                   ← 🟢 Reachability & latency
│   ├── test_api_contract.py            ← 🔵 Response shape & parsing
│   ├── test_regression_baseline.py     ← 🟡 Answer + context presence
│   ├── test_context_precision.py       ← 🟡 Retrieval relevance score
│   ├── test_faithfulness.py            ← 🟡 Grounding score
│   ├── test_answer_relevancy.py        ← 🟡 Question-answer fit score
│   ├── test_context_recall.py          ← 🟡 Retrieval coverage score
│   └── test_negative_cases.py         ← 🔴 Malformed / bad response detection
└── 🔄 .github/
    └── workflows/
        └── qa.yml                      ← GitHub Actions CI workflow
```

---

## 📋 File-By-File Explanation

### 🔧 Root Files

| File | Purpose |
|------|---------|
| `.env.example` | Template showing required env vars — models, thresholds, timeouts, paths |
| `.gitignore` | Ignores `.env`, virtual environments, caches, and generated reports |
| `pyproject.toml` | Makes the framework installable with `pip install -e .`; registers `src/` discovery |
| `pytest.ini` | Enables async mode, limits discovery to `tests/`, registers markers |

---

### 🗃️ Dataset

#### `datasets/test_cases.json`
Stores benchmark questions and reference answers **outside the code** so you can expand coverage without touching test logic.

---

### 🧠 Source Code

#### `src/aiqa_testing/config.py`
> 🎛️ **Central control panel** — all thresholds, timeouts, paths, and model names in one place.

#### `src/aiqa_testing/models.py`
> 🏗️ **Typed API models** — validates `/ask` response structure and provides clear errors for malformed payloads.

#### `src/aiqa_testing/datasets.py`
> 📥 **Dataset loader** — reads JSON into typed `TestCase` objects, keeping fixtures clean.

#### `src/aiqa_testing/client.py`
> 🌐 **API client** — calls the RAG API, measures latency, applies retry logic, and builds the `ragas` evaluator LLM + embeddings.

#### `src/aiqa_testing/sample_builder.py`
> 🧩 **Sample builder** — extracts retrieved contexts and builds `SingleTurnSample` objects for metric tests.

#### `src/aiqa_testing/reporting.py`
> 📊 **Report writer** — captures metric results and test outcomes into a machine-readable JSON summary.

---

### 🧪 Tests

| File | Marker | What It Tests |
|------|--------|---------------|
| `test_data.py` | — | Dataset not empty; case IDs are unique |
| `test_smoke.py` | 🟢 `smoke` | API reachable; latency within budget |
| `test_api_contract.py` | 🔵 `contract` | Valid payload parsing; malformed payloads fail clearly |
| `test_regression_baseline.py` | 🟡 `regression` | Every benchmark question returns an answer with context |
| `test_context_precision.py` | 🟡 `regression` | Retrieved context is relevant enough to support the answer |
| `test_faithfulness.py` | 🟡 `regression` | Answer is grounded in context — not fabricated |
| `test_answer_relevancy.py` | 🟡 `regression` | Answer actually addresses the user's question |
| `test_context_recall.py` | 🟡 `regression` | Retrieval step didn't miss important context |
| `test_negative_cases.py` | 🔴 `negative` | Empty answers and bad documents are rejected |

---

### 🔄 CI

#### `.github/workflows/qa.yml`
Automatically installs the project, runs the full suite, and uploads report artifacts on every push.

---

### 📊 Reports

#### `reports/latest-summary.json`
Generated at the end of every test session. Contains:
- Aggregate pass/fail counts
- Per-metric scores
- Machine-readable run summary for CI comparisons

---

## 🚦 Test Categories

### 🟢 Smoke Tests — *"Is it alive?"*
Fast operational checks. Run these first.
```powershell
pytest -m smoke
```

### 🔵 Contract Tests — *"Is the API shape correct?"*
Validate response structure and parsing behaviour.
```powershell
pytest -m contract
```

### 🟡 Regression Tests — *"Is the quality holding up?"*
Core quality tests against the live RAG system.
```powershell
pytest -m regression
```

### 🔴 Negative Tests — *"Does it reject bad responses?"*
Confirm malformed or weak responses are detected.
```powershell
pytest -m negative
```

---

## 🚀 Running The Project

### 1️⃣ Set up the environment
```powershell
cd C:\Users\mvsar\PycharmProjects\LLMEvaluation\AIQATestingFramework
python -m venv .venv
.venv\Scripts\activate
pip install -e .
```

### 2️⃣ Run the full suite
```powershell
pytest
```

### 3️⃣ Run a specific test file
```powershell
pytest tests\test_smoke.py
pytest tests\test_regression_baseline.py
pytest tests\test_context_precision.py
```

### 4️⃣ Generate HTML + JUnit reports
```powershell
pytest --html reports\report.html --self-contained-html --junitxml reports\junit.xml
```

---

## 🌡️ ragas Metrics at a Glance

| Metric | What It Measures | Default Threshold |
|--------|-----------------|:-----------------:|
| 🎯 **Answer Relevancy** | Does the answer address the question? | `≥ 0.70` |
| ⚓ **Faithfulness** | Is the answer grounded in retrieved context? | `≥ 0.70` |
| 🔍 **Context Precision** | Is the retrieved context relevant? | `≥ 0.70` |
| 📡 **Context Recall** | Did retrieval cover all important context? | `≥ 0.70` |

> 💡 **Tip:** Fix retrieval quality first. Improving context recall from 70 % → 90 % often boosts answer quality automatically — before touching the LLM.

---

## 🔐 Environment Variables

```env
# 🔑 API Keys
OPENAI_API_KEY=your_key_here

# 🌐 RAG API
RAG_API_BASE_URL=http://localhost:8000
RAG_TOP_K=3
RAG_TIMEOUT_SECONDS=30

# 🤖 Evaluator Models
EVALUATOR_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small

# 🚦 Pass/Fail Thresholds
THRESHOLD_CONTEXT_PRECISION=0.70
THRESHOLD_FAITHFULNESS=0.70
THRESHOLD_ANSWER_RELEVANCY=0.70
THRESHOLD_CONTEXT_RECALL=0.70

# ⚡ Latency
SMOKE_MAX_LATENCY_MS=8000

# 📂 Paths
AIQA_REPORT_FILE=reports/latest-summary.json
AIQA_DATASET_PATH=datasets/test_cases.json
```

---

## 🏗️ Architecture at a Glance

```
┌─────────────────────────────────────────────────────────┐
│                  AIQATestingFramework                   │
│                                                         │
│  📂 Dataset  ──►  🌐 API Client  ──►  🧩 Sample Builder │
│                        │                               │
│                        ▼                               │
│              📊 ragas Evaluator                        │
│          (Faithfulness · Relevancy ·                   │
│           Precision · Recall)                          │
│                        │                               │
│                        ▼                               │
│           🚦 Threshold Gate  ──►  ✅ PASS / ❌ FAIL    │
│                        │                               │
│                        ▼                               │
│           📝 JSON Report  +  🔄 CI Artifact            │
└─────────────────────────────────────────────────────────┘
```

---

## 📌 Summary

**`AIQATestingFramework`** is a standalone, modular quality gate for RAG APIs.

It separates every concern into its own layer:

- 📥 **Dataset loading** — `datasets.py`
- 🌐 **API calls** — `client.py`
- 🏗️ **Typed validation** — `models.py`
- 📊 **Metric scoring** — `ragas` via `sample_builder.py`
- 📝 **Reporting** — `reporting.py`
- 🔄 **CI automation** — `qa.yml`

Drop in new test cases, adjust thresholds, and plug into any CI pipeline — no changes to test logic required.

---

*Generated by AIQATestingFramework · Powered by `ragas` + `pytest`*
