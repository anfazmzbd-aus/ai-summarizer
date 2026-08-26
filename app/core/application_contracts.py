"""V11 application-level summarization contracts."""

from __future__ import annotations

from dataclasses import dataclass
from app.core.application_metadata import SummarizationExecutionMetadata


@dataclass(frozen=True)
class SummarizationApplicationRequest:
    """
    Canonical application-level summarization request.

    This contract isolates the public API from V9 summarization and
    V10 intelligence implementation models.
    """

    text: str
    provider: str | None = None
    model: str | None = None
    prompt_name: str | None = None


@dataclass(frozen=True)
class SummarizationApplicationResult:
    """
    Canonical application-level summarization result.

    M1.4 intentionally exposes only product-facing output required by
    the current API. Later milestones may add explicitly approved
    read-only metadata without leaking runtime-domain objects.
    """

    summary: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    metadata: SummarizationExecutionMetadata = SummarizationExecutionMetadata()

    @property
    def total_tokens(self) -> int:
        """Return total token usage."""

        return self.prompt_tokens + self.completion_tokens
