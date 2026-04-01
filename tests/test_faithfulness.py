import pytest
from ragas.metrics.collections import Faithfulness

from aiqa_testing.client import call_ask_api
from aiqa_testing.sample_builder import build_single_turn_sample


@pytest.mark.regression
@pytest.mark.asyncio
async def test_faithfulness(
    settings,
    test_case,
    evaluator_llm,
    require_rag_api,
    record_metric,
):
    response = call_ask_api(test_case.question, settings)
    sample = build_single_turn_sample(test_case, response)

    metric = Faithfulness(llm=evaluator_llm)
    result = await metric.ascore(
        user_input=sample.user_input,
        response=sample.response,
        retrieved_contexts=sample.retrieved_contexts,
    )
    score = result.value
    threshold = settings.threshold_faithfulness
    record_metric("faithfulness", test_case, score, threshold)

    assert score is not None, "Faithfulness score is None."
    assert score >= threshold, (
        f"Faithfulness too low for '{test_case.question}'. "
        f"Expected >= {threshold}, got {score}"
    )
