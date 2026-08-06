"""
AI Summarizer V9.0

Provider domain models.

These immutable models define the common request/response contracts used by
all LLM providers (OpenAI, Azure OpenAI, Ollama, and future providers).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping


class MessageRole(str, Enum):
    """Supported chat message roles."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class FinishReason(str, Enum):
    """Reason why model generation completed."""

    STOP = "stop"
    LENGTH = "length"
    TOOL_CALLS = "tool_calls"
    CONTENT_FILTER = "content_filter"
    ERROR = "error"


@dataclass(slots=True, frozen=True)
class LLMMessage:
    """
    Represents a single message in a chat conversation.
    """

    role: MessageRole
    content: str
    name: str | None = None


@dataclass(slots=True, frozen=True)
class Usage:
    """
    Token usage statistics returned by a provider.
    """

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


@dataclass(slots=True, frozen=True)
class LLMRequest:
    """
    Provider-independent chat request.
    """

    messages: tuple[LLMMessage, ...]

    model: str

    temperature: float = 0.2

    max_tokens: int | None = None

    stream: bool = False

    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class LLMResponse:
    """
    Provider-independent chat response.
    """

    message: LLMMessage

    model: str

    finish_reason: FinishReason

    usage: Usage

    latency_ms: float

    metadata: Mapping[str, Any] = field(default_factory=dict)
