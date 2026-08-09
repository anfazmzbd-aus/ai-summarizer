"""
AI Summarizer V9.x

Summary agent.

Supports two execution modes:

1. Legacy mode
   Preserves the V8-compatible deterministic behavior.

2. AI mode
   Uses the V9 PromptManager + LLMService pipeline.
"""

from __future__ import annotations

from typing import Any

from app.providers.models import (
    LLMMessage,
    LLMRequest,
    MessageRole,
)
from app.prompts.value_objects import (
    PromptId,
    PromptVersion,
)


class SummaryAgent:
    """
    Summary execution agent.

    When V9 runtime dependencies are supplied, the agent executes through
    PromptManager and LLMService.

    When no dependencies are supplied, it preserves the legacy V8 behavior.
    """

    def __init__(
        self,
        *,
        prompt_manager: Any | None = None,
        prompt_id: PromptId | None = None,
        prompt_version: PromptVersion | None = None,
        model: str | None = None,
        llm_service: Any | None = None,
    ) -> None:
        self._prompt_manager = prompt_manager
        self._prompt_id = prompt_id
        self._prompt_version = prompt_version
        self._model = model
        self._llm_service = llm_service

    @classmethod
    def legacy(cls) -> "SummaryAgent":
        """
        Create a legacy V8-compatible SummaryAgent.
        """
        return cls()

    @property
    def is_ai_enabled(self) -> bool:
        """
        Return whether the V9 AI execution path is configured.
        """
        return all(
            value is not None
            for value in (
                self._prompt_manager,
                self._prompt_id,
                self._prompt_version,
                self._model,
                self._llm_service,
            )
        )

    def run(self, data) -> dict[str, str]:
        """
        Execute summary generation.

        AI mode is selected when all required V9 dependencies are present.
        Otherwise the V8-compatible deterministic behavior is used.
        """
        if self.is_ai_enabled:
            return self._run_ai(data)

        return self._run_legacy(data)

    def _run_ai(self, data) -> dict[str, str]:
        """
        Execute the V9 prompt → LLM service pipeline.
        """
        text = data.global_context["text"]

        rendered_prompt = self._prompt_manager.render(
            prompt_id=self._prompt_id,
            version=self._prompt_version,
            variables={
                "text": text,
            },
        )

        request = LLMRequest(
            messages=(
                LLMMessage(
                    role=MessageRole.SYSTEM,
                    content=rendered_prompt.system_prompt,
                ),
                LLMMessage(
                    role=MessageRole.USER,
                    content=rendered_prompt.user_prompt,
                ),
            ),
            model=self._model,
        )

        response = self._llm_service.execute(request)

        summary = response.message.content.strip()

        return {
            "summary": summary,
        }

    @staticmethod
    def _run_legacy(data) -> dict[str, str]:
        """
        Preserve the existing V8 SummaryAgent behavior.
        """
        text = data.global_context["text"]

        return {
            "summary": text[:150],
        }
