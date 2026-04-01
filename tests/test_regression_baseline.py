import pytest

from aiqa_testing.client import call_ask_api
from aiqa_testing.sample_builder import extract_retrieved_contexts


@pytest.mark.regression
def test_regression_baseline_response_quality(settings, test_case, require_rag_api):
    response = call_ask_api(test_case.question, settings)
    retrieved_contexts = extract_retrieved_contexts(response)

    assert response.question == test_case.question
    assert response.answer.strip(), f"Expected a non-empty answer for '{test_case.question}'"
    assert retrieved_contexts, f"Expected retrieved contexts for '{test_case.question}'"
    assert any(
        context.strip() for context in retrieved_contexts
    ), f"Expected at least one non-empty retrieved context for '{test_case.question}'"
