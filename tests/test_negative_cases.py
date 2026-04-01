import pytest

from aiqa_testing.models import AskAPIResponse
from aiqa_testing.sample_builder import extract_retrieved_contexts


@pytest.mark.negative
def test_empty_answer_is_rejected():
    with pytest.raises(ValueError, match="answer"):
        AskAPIResponse.from_dict(
            {
                "question": "What is RAG?",
                "answer": "   ",
                "documents": [{"page_content": "RAG content"}],
            }
        )


@pytest.mark.negative
def test_missing_documents_are_rejected():
    with pytest.raises(ValueError, match="documents"):
        AskAPIResponse.from_dict(
            {
                "question": "What is RAG?",
                "answer": "RAG answer",
            }
        )


@pytest.mark.negative
def test_non_object_document_is_rejected():
    with pytest.raises(ValueError, match="document"):
        AskAPIResponse.from_dict(
            {
                "question": "What is RAG?",
                "answer": "RAG answer",
                "documents": ["bad-doc"],
            }
        )


@pytest.mark.negative
def test_irrelevant_documents_still_parse_but_can_be_detected():
    response = AskAPIResponse.from_dict(
        {
            "question": "What is RAG?",
            "answer": "RAG is about retrieval.",
            "documents": [{"page_content": "This text is about cooking recipes and nothing else."}],
        }
    )

    contexts = extract_retrieved_contexts(response)
    assert contexts == ["This text is about cooking recipes and nothing else."]
    assert "retrieval" not in contexts[0].lower()
