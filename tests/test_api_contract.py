import pytest

from aiqa_testing.client import call_ask_api
from aiqa_testing.models import AskAPIResponse, DocumentRecord


@pytest.mark.contract
def test_typed_response_model_accepts_valid_payload():
    response = AskAPIResponse.from_dict(
        {
            "question": "What is RAG?",
            "answer": "RAG uses retrieved context.",
            "documents": [{"page_content": "RAG retrieves supporting content.", "metadata": {"source": "doc"}}],
        }
    )

    assert response.question == "What is RAG?"
    assert response.answer == "RAG uses retrieved context."
    assert response.documents[0] == DocumentRecord(
        page_content="RAG retrieves supporting content.",
        metadata={"source": "doc"},
    )


@pytest.mark.contract
def test_contract_live_response_matches_expected_shape(settings, require_rag_api):
    response = call_ask_api("What is an AI Agent?", settings)
    assert isinstance(response, AskAPIResponse)
    assert response.question
    assert response.answer
    assert response.documents


@pytest.mark.contract
@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"question": "", "answer": "ok", "documents": [{"page_content": "x"}]},
        {"question": "q", "answer": "", "documents": [{"page_content": "x"}]},
        {"question": "q", "answer": "a", "documents": []},
        {"question": "q", "answer": "a", "documents": [{"page_content": ""}]},
    ],
)
def test_invalid_payloads_raise_clear_errors(payload):
    with pytest.raises(ValueError):
        AskAPIResponse.from_dict(payload)
