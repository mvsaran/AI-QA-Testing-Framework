import pytest
from ragas.metrics.collections import AnswerRelevancy

from aiqa_testing.client import call_ask_api
from aiqa_testing.sample_builder import build_single_turn_sample


@pytest.mark.regression
@pytest.mark.asyncio
async def test_answer_relevancy(
    settings,
    test_case,
    evaluator_llm,
    embeddings,
    require_rag_api,
    record_metric,
):
    response = call_ask_api(test_case.question, settings)
    sample = build_single_turn_sample(test_case, response)

    metric = AnswerRelevancy(
        llm=evaluator_llm,
        embeddings=embeddings,
    )
    result = await metric.ascore(
        user_input=sample.user_input,
        response=sample.response,
    )
    score = result.value
    threshold = settings.threshold_answer_relevancy
    record_metric("answer_relevancy", test_case, score, threshold)

    assert score is not None, "Answer relevancy score is None."
    assert score >= threshold, (
        f"Answer relevancy too low for '{test_case.question}'. "
        f"Expected >= {threshold}, got {score}"
    )
