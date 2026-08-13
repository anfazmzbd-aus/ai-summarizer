"""
Tests for V9.2 test infrastructure.
"""

from __future__ import annotations

from app.tests.fixtures.mock_llm import (
    MockLLMProvider,
    collect_stream,
    make_mock_response,
)


def test_mock_provider_is_deterministic():
    provider = MockLLMProvider(response="Deterministic summary")

    response = provider.summarize("Summarize this document.")

    assert response.content == "Deterministic summary"
    assert response.model == "mock-model"


def test_mock_provider_records_calls():
    provider = MockLLMProvider()

    provider.summarize(
        "Test prompt",
        model="test-model",
        temperature=0,
    )

    assert provider.call_count == 1

    call = provider.last_call()

    assert call["prompt"] == "Test prompt"
    assert call["model"] == "test-model"
    assert call["kwargs"] == {"temperature": 0}


def test_mock_provider_supports_multiple_calls():
    provider = MockLLMProvider()

    provider.summarize("First")
    provider.summarize("Second")

    assert provider.call_count == 2
    assert provider.calls[0]["prompt"] == "First"
    assert provider.calls[1]["prompt"] == "Second"


def test_mock_provider_stream_is_deterministic():
    provider = MockLLMProvider(response="This is a streamed summary")

    events = list(provider.stream("Summarize"))

    assert [event.index for event in events] == [
        0,
        1,
        2,
        3,
        4,
    ]

    assert collect_stream(events) == ("This is a streamed summary")


def test_stream_call_is_recorded():
    provider = MockLLMProvider(response="stream response")

    list(
        provider.stream(
            "Prompt",
            model="stream-model",
        )
    )

    assert provider.call_count == 1

    call = provider.last_call()

    assert call["stream"] is True
    assert call["model"] == "stream-model"


def test_make_mock_response():
    response = make_mock_response(
        content="Expected result",
        model="test-model",
    )

    assert response.content == "Expected result"
    assert response.model == "test-model"


def test_mock_provider_never_requires_api_credentials():
    provider = MockLLMProvider(response="No network required")

    response = provider.summarize("Test")

    assert response.content == "No network required"
