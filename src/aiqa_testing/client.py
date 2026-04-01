from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

import requests
from openai import AsyncOpenAI
from ragas.embeddings import OpenAIEmbeddings
from ragas.llms import llm_factory
from requests import Response
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .config import Settings
from .models import AskAPIResponse


@dataclass(frozen=True)
class TimedAPIResponse:
    payload: AskAPIResponse
    latency_ms: float
    status_code: int


def get_openai_key() -> str:
    import os

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY is missing in your environment or .env file.")
    return api_key


def create_retry_session() -> requests.Session:
    session = requests.Session()
    retries = Retry(
        total=2,
        connect=2,
        read=2,
        backoff_factor=0.5,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset({"GET", "POST"}),
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def build_evaluator_llm(settings: Settings):
    client = AsyncOpenAI(api_key=get_openai_key())
    return llm_factory(
        settings.evaluator_model,
        provider="openai",
        client=client,
        temperature=0,
    )


def build_embeddings(settings: Settings):
    client = AsyncOpenAI(api_key=get_openai_key())
    return OpenAIEmbeddings(
        client=client,
        model=settings.embedding_model,
    )


def is_rag_api_available(settings: Settings) -> bool:
    session = create_retry_session()
    try:
        response = session.get(settings.rag_api_base_url, timeout=3)
        return response.status_code < 500
    except requests.RequestException:
        return False


def _raise_for_invalid_status(response: Response) -> None:
    response.raise_for_status()


def call_ask_api(question: str, settings: Settings) -> AskAPIResponse:
    return call_ask_api_timed(question=question, settings=settings).payload


def call_ask_api_timed(question: str, settings: Settings) -> TimedAPIResponse:
    session = create_retry_session()
    start = time.perf_counter()
    response = session.post(
        f"{settings.rag_api_base_url}/ask",
        json={
            "question": question,
            "chat_history": [],
            "top_k": settings.rag_top_k,
        },
        timeout=settings.rag_timeout_seconds,
    )
    latency_ms = (time.perf_counter() - start) * 1000
    _raise_for_invalid_status(response)
    payload: dict[str, Any] = response.json()
    typed_response = AskAPIResponse.from_dict(payload)
    return TimedAPIResponse(
        payload=typed_response,
        latency_ms=latency_ms,
        status_code=response.status_code,
    )
