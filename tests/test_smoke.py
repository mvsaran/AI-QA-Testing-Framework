import pytest

from aiqa_testing.client import call_ask_api_timed


@pytest.mark.smoke
def test_rag_api_is_reachable(require_rag_api):
    assert require_rag_api is None


@pytest.mark.smoke
def test_rag_api_latency_is_within_budget(settings, require_rag_api):
    timed_response = call_ask_api_timed("What is an AI Agent?", settings)
    assert timed_response.status_code == 200
    assert timed_response.latency_ms <= settings.smoke_max_latency_ms, (
        f"Latency budget exceeded. Expected <= {settings.smoke_max_latency_ms} ms, "
        f"got {timed_response.latency_ms:.2f} ms"
    )
