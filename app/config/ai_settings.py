"""
AI runtime settings.
"""

from __future__ import annotations

import os

from dataclasses import dataclass, field


@dataclass(slots=True)
class AISettings:

    provider: str = field(
        default_factory=lambda: os.getenv(
            "AI_PROVIDER",
            "fake",
        )
    )

    api_key: str = field(
        default_factory=lambda: os.getenv(
            "OPENAI_API_KEY",
            "",
        ),
        repr=False,
    )

    model: str = field(
        default_factory=lambda: os.getenv(
            "OPENAI_MODEL",
            "gpt-5-mini",
        )
    )

    base_url: str | None = field(
        default_factory=lambda: (
            os.getenv(
                "OPENAI_BASE_URL",
            )
            or None
        )
    )

    organization: str | None = field(
        default_factory=lambda: (
            os.getenv(
                "OPENAI_ORGANIZATION",
            )
            or None
        )
    )
