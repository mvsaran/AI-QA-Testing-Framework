from __future__ import annotations

from ragas import SingleTurnSample

from .models import AskAPIResponse, TestCase


def extract_retrieved_contexts(response: AskAPIResponse) -> list[str]:
    return [document.page_content for document in response.documents]


def build_single_turn_sample(test_case: TestCase, response: AskAPIResponse) -> SingleTurnSample:
    retrieved_contexts = extract_retrieved_contexts(response)
    if not retrieved_contexts:
        raise ValueError("No retrieved contexts extracted from API response.")

    return SingleTurnSample(
        user_input=test_case.question,
        response=response.answer,
        retrieved_contexts=retrieved_contexts,
        reference=test_case.reference,
    )
