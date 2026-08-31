"""
V11 M6.4 controlled live-provider validation.

This module validates the canonical V11 product path against a real
OpenAI-compatible provider only when live execution is explicitly enabled.

Normal test execution must remain offline.
"""

from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

from app.main import app

from dotenv import dotenv_values

pytestmark = [
    pytest.mark.integration,
    pytest.mark.live,
]


_dotenv = dotenv_values(".env")

OPENROUTER_API_KEY = (
    os.getenv("OPENROUTER_API_KEY") or _dotenv.get("OPENROUTER_API_KEY") or ""
)

OPENROUTER_BASE_URL = (
    os.getenv("OPENROUTER_BASE_URL")
    or _dotenv.get("OPENROUTER_BASE_URL")
    or "https://openrouter.ai/api/v1"
)

OPENROUTER_MODEL = (
    os.getenv("OPENROUTER_MODEL")
    or _dotenv.get("OPENROUTER_MODEL")
    or "openai/gpt-5-mini"
)


@pytest.mark.skipif(
    not OPENROUTER_API_KEY,
    reason="OPENROUTER_API_KEY is required for live provider validation",
)
def test_canonical_summarize_executes_through_live_openai_compatible_provider(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "AI_PROVIDER",
        "openai",
    )
    monkeypatch.setenv(
        "OPENAI_API_KEY",
        OPENROUTER_API_KEY,
    )
    monkeypatch.setenv(
        "OPENAI_BASE_URL",
        OPENROUTER_BASE_URL,
    )
    monkeypatch.setenv(
        "OPENAI_MODEL",
        OPENROUTER_MODEL,
    )

    client = TestClient(app)

    response = client.post(
        "/api/v1/summarize",
        json={
            "text": (
                "Artificial intelligence can help software teams "
                "summarize operational information efficiently."
            ),
            "provider": "openai",
            "model": OPENROUTER_MODEL,
        },
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["summary"]
    assert payload["model"] == OPENROUTER_MODEL

    assert payload["prompt_tokens"] >= 0
    assert payload["completion_tokens"] >= 0
    assert payload["total_tokens"] >= 0

    assert payload["metadata"]["strategy"]
    assert payload["metadata"]["intelligence_mode"] == "preserve"
