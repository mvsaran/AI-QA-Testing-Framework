import pytest
from ragas.metrics.collections import ContextRecall

from aiqa_testing.client import call_ask_api
from aiqa_testing.sample_builder import build_single_turn_sample


@pytest.mark.regression
@pytest.mark.asyncio
async def test_context_recall(
    settings,
    test_case,
    evaluator_llm,
    require_rag_api,
    record_metric,
):
    response = call_ask_api(test_case.question, settings)
    sample = build_single_turn_sample(test_case, response)

    metric = ContextRecall(llm=evaluator_llm)
    result = await metric.ascore(
        user_input=sample.user_input,
        reference=sample.reference,
        retrieved_contexts=sample.retrieved_contexts,
    )
    score = result.value
    threshold = settings.threshold_context_recall
    record_metric("context_recall", test_case, score, threshold)

    assert score is not None, "Context recall score is None."
    assert score >= threshold, (
        f"Context recall too low for '{test_case.question}'. "
        f"Expected >= {threshold}, got {score}"
    )
