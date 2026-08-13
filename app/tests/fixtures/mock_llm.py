"""
Deterministic mock LLM components for tests.

These components deliberately do not perform network access.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Iterator


@dataclass(frozen=True)
class MockLLMResponse:
    """Deterministic mock LLM response."""

    content: str
    model: str = "mock-model"
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


@dataclass(frozen=True)
class MockStreamEvent:
    """One deterministic streaming event."""

    content: str
    index: int


class MockLLMProvider:
    """
    Deterministic provider double.

    Records every invocation so tests can verify provider interaction
    without making external API calls.
    """

    def __init__(
        self,
        response: str = "Mock summary",
        model: str = "mock-model",
    ) -> None:
        self.response = response
        self.model = model
        self.calls: list[dict[str, object]] = []

    def summarize(
        self,
        prompt: str,
        *,
        model: str | None = None,
        **kwargs: object,
    ) -> MockLLMResponse:
        """Return a deterministic response."""
        self.calls.append(
            {
                "prompt": prompt,
                "model": model or self.model,
                "kwargs": kwargs,
            }
        )

        return MockLLMResponse(
            content=self.response,
            model=model or self.model,
        )

    def stream(
        self,
        prompt: str,
        *,
        model: str | None = None,
        **kwargs: object,
    ) -> Iterator[MockStreamEvent]:
        """Yield deterministic streaming events."""
        self.calls.append(
            {
                "prompt": prompt,
                "model": model or self.model,
                "kwargs": kwargs,
                "stream": True,
            }
        )

        words = self.response.split()

        for index, word in enumerate(words):
            yield MockStreamEvent(
                content=word,
                index=index,
            )

    @property
    def call_count(self) -> int:
        """Return the number of provider invocations."""
        return len(self.calls)

    def last_call(self) -> dict[str, object]:
        """Return the most recent provider invocation."""
        if not self.calls:
            raise AssertionError("No provider calls were recorded.")

        return self.calls[-1]


def make_mock_response(
    content: str = "Mock summary",
    model: str = "mock-model",
) -> MockLLMResponse:
    """Create a deterministic mock response."""
    return MockLLMResponse(
        content=content,
        model=model,
    )


def collect_stream(
    events: Iterable[MockStreamEvent],
) -> str:
    """Combine deterministic stream events into text."""
    return " ".join(event.content for event in events)
