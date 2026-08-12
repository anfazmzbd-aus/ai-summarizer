import os
from dotenv import load_dotenv
import pytest

from app.providers.config import ProviderType
from app.providers.factory import ProviderFactory
from app.providers.models import (
    LLMMessage,
    LLMRequest,
    MessageRole,
)
from app.providers.runtime import ProviderRuntime

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

OPENROUTER_BASE_URL = os.getenv(
    "OPENROUTER_BASE_URL",
    "https://openrouter.ai/api/v1",
)

OPENROUTER_MODEL = os.getenv(
    "OPENROUTER_MODEL",
    "openai/gpt-5",
)


pytestmark = pytest.mark.integration


@pytest.fixture
def openrouter_runtime():
    if not OPENROUTER_API_KEY:
        pytest.skip("OPENROUTER_API_KEY is not configured.")

    factory = ProviderFactory()

    return ProviderRuntime.openai(
        factory,
        api_key=OPENROUTER_API_KEY,
        model=OPENROUTER_MODEL,
        endpoint=OPENROUTER_BASE_URL,
    )


def test_live_openrouter_provider_type(
    openrouter_runtime,
):
    assert openrouter_runtime.provider_type is ProviderType.OPENAI

    assert openrouter_runtime.provider_name == "openai"


def test_live_openrouter_execution(
    openrouter_runtime,
):
    request = LLMRequest(
        model=OPENROUTER_MODEL,
        messages=(
            LLMMessage(
                role=MessageRole.USER,
                content=("Reply with exactly: " "LIVE_OPENROUTER_OK"),
            ),
        ),
    )

    response = openrouter_runtime.service.execute(request)

    assert response is not None
    assert response.message.content

    assert "LIVE_OPENROUTER_OK" in response.message.content


def test_live_openrouter_usage(
    openrouter_runtime,
):
    request = LLMRequest(
        model=OPENROUTER_MODEL,
        messages=(
            LLMMessage(
                role=MessageRole.USER,
                content="Say hello.",
            ),
        ),
    )

    response = openrouter_runtime.service.execute(request)

    assert response.usage is not None
    assert response.usage.prompt_tokens > 0
    assert response.usage.completion_tokens > 0
    assert response.usage.total_tokens >= (response.usage.prompt_tokens)
    assert response.usage.total_tokens >= (response.usage.completion_tokens)


def test_live_openrouter_latency(
    openrouter_runtime,
):
    request = LLMRequest(
        model=OPENROUTER_MODEL,
        messages=(
            LLMMessage(
                role=MessageRole.USER,
                content="Say hello.",
            ),
        ),
    )

    response = openrouter_runtime.service.execute(request)

    assert response.latency_ms > 0
