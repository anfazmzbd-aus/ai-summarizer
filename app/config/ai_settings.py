"""
AI runtime settings.
"""

from __future__ import annotations

import os

from dataclasses import dataclass


@dataclass(slots=True)
class AISettings:

    provider: str = os.getenv(
        "AI_PROVIDER",
        "fake",
    )

    api_key: str = os.getenv(
        "OPENAI_API_KEY",
        "",
    )

    model: str = os.getenv(
        "OPENAI_MODEL",
        "gpt-5-mini",
    )

    base_url: str | None = (
        os.getenv(
            "OPENAI_BASE_URL",
        )
        or None
    )

    organization: str | None = (
        os.getenv(
            "OPENAI_ORGANIZATION",
        )
        or None
    )
