"""
AI Summarizer V9.1

Environment-backed provider settings.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from app.providers.config import ProviderType


@dataclass(frozen=True, slots=True)
class ProviderSettings:
    provider: ProviderType = ProviderType.MOCK
    model: str = "mock-model"
    api_key: str | None = None
    endpoint: str | None = None
    organization: str | None = None
    timeout: float = 60.0
    max_retries: int = 2

    @classmethod
    def from_environment(cls) -> "ProviderSettings":
        provider_value = (
            os.getenv(
                "AI_PROVIDER",
                ProviderType.MOCK.value,
            )
            .strip()
            .lower()
        )

        try:
            provider = ProviderType(provider_value)
        except ValueError as exc:
            raise ValueError(f"Unsupported AI_PROVIDER: {provider_value}") from exc

        model = os.getenv(
            "AI_MODEL",
            "mock-model",
        ).strip()

        if not model:
            raise ValueError("AI_MODEL cannot be empty.")

        api_key = os.getenv("AI_API_KEY")

        endpoint = os.getenv("AI_PROVIDER_ENDPOINT")

        organization = os.getenv("AI_PROVIDER_ORGANIZATION")

        timeout = float(
            os.getenv(
                "AI_PROVIDER_TIMEOUT",
                "60",
            )
        )

        max_retries = int(
            os.getenv(
                "AI_PROVIDER_MAX_RETRIES",
                "2",
            )
        )

        if timeout <= 0:
            raise ValueError("AI_PROVIDER_TIMEOUT must be positive.")

        if max_retries < 0:
            raise ValueError("AI_PROVIDER_MAX_RETRIES cannot be negative.")

        return cls(
            provider=provider,
            model=model,
            api_key=api_key,
            endpoint=endpoint,
            organization=organization,
            timeout=timeout,
            max_retries=max_retries,
        )
