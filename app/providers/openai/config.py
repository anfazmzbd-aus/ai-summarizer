from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class OpenAIConfig:
    """
    Production configuration.
    """

    api_key: str

    model: str = "gpt-5"

    organization: str | None = None

    base_url: str | None = None

    timeout: float = 60.0

    max_retries: int = 2

    def __post_init__(self) -> None:

        if not self.api_key.strip():
            raise ValueError("OpenAI API key cannot be empty.")

        if self.timeout <= 0:
            raise ValueError("Timeout must be positive.")

        if self.max_retries < 0:
            raise ValueError("Retries cannot be negative.")
