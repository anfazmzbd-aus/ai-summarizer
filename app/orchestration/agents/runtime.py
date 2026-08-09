"""
AI Summarizer V9.1

Agent runtime dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.prompts.manager import PromptManager
    from app.prompts.value_objects import PromptId, PromptVersion
    from app.services.llm_service import LLMService


@dataclass(frozen=True, slots=True)
class AgentRuntime:
    """
    Dependencies required by provider-backed agents.
    """

    prompt_manager: "PromptManager"
    llm_service: "LLMService"
    prompt_id: "PromptId"
    prompt_version: "PromptVersion"
    model: str
