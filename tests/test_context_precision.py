import pytest
from ragas.metrics.collections import ContextPrecisionWithReference

from aiqa_testing.client import call_ask_api
from aiqa_testing.sample_builder import build_single_turn_sample


@pytest.mark.regression
@pytest.mark.asyncio
async def test_context_precision(
    settings,
    test_case,
    evaluator_llm,
    require_rag_api,
    record_metric,
):
    response = call_ask_api(test_case.question, settings)
    sample = build_single_turn_sample(test_case, response)

    metric = ContextPrecisionWithReference(llm=evaluator_llm)
    result = await metric.ascore(
        user_input=sample.user_input,
        reference=sample.reference,
        retrieved_contexts=sample.retrieved_contexts,
    )
    score = result.value
    threshold = settings.threshold_context_precision
    record_metric("context_precision", test_case, score, threshold)

    assert score is not None, "Context precision score is None."
    assert score >= threshold, (
        f"Context precision too low for '{test_case.question}'. "
        f"Expected >= {threshold}, got {score}"
    )
