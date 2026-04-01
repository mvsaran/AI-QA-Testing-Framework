from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class DocumentRecord:
    page_content: str
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "DocumentRecord":
        page_content = payload.get("page_content")
        if not isinstance(page_content, str) or not page_content.strip():
            raise ValueError("Each document must contain non-empty string field 'page_content'.")

        metadata = payload.get("metadata", {})
        if metadata is None:
            metadata = {}
        if not isinstance(metadata, dict):
            raise ValueError("Document 'metadata' must be a dictionary when provided.")

        return cls(page_content=page_content.strip(), metadata=metadata)


@dataclass(frozen=True)
class AskAPIResponse:
    question: str
    answer: str
    documents: list[DocumentRecord]

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "AskAPIResponse":
        question = payload.get("question")
        answer = payload.get("answer")
        documents = payload.get("documents")

        if not isinstance(question, str) or not question.strip():
            raise ValueError("Response must include non-empty string field 'question'.")
        if not isinstance(answer, str) or not answer.strip():
            raise ValueError("Response must include non-empty string field 'answer'.")
        if not isinstance(documents, list) or not documents:
            raise ValueError("Response must include non-empty list field 'documents'.")

        typed_documents = []
        for document in documents:
            if not isinstance(document, dict):
                raise ValueError("Each document in 'documents' must be an object.")
            typed_documents.append(DocumentRecord.from_dict(document))

        return cls(
            question=question.strip(),
            answer=answer.strip(),
            documents=typed_documents,
        )


@dataclass(frozen=True)
class TestCase:
    case_id: str
    question: str
    reference: str

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "TestCase":
        case_id = payload.get("id")
        question = payload.get("question")
        reference = payload.get("reference")

        if not isinstance(case_id, str) or not case_id.strip():
            raise ValueError("Each test case must include non-empty string field 'id'.")
        if not isinstance(question, str) or not question.strip():
            raise ValueError("Each test case must include non-empty string field 'question'.")
        if not isinstance(reference, str) or not reference.strip():
            raise ValueError("Each test case must include non-empty string field 'reference'.")

        return cls(case_id=case_id.strip(), question=question.strip(), reference=reference.strip())
