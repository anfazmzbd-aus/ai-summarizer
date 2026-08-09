"""
AI Summarizer V9.0

Prompt domain models.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from .value_objects import (
    PromptId,
    PromptVariable,
    PromptVersion,
)


@dataclass(frozen=True, slots=True)
class PromptMetadata:
    """
    Prompt ownership and lifecycle metadata.
    """

    prompt_id: PromptId

    version: PromptVersion

    description: str

    author: str

    tags: tuple[str, ...] = ()

    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True, slots=True)
class PromptDefinition:
    """
    Complete prompt definition.

    This represents a versioned prompt asset.
    """

    metadata: PromptMetadata

    system_template: str

    user_template: str

    variables: tuple[PromptVariable, ...] = ()

    @classmethod
    def create(
        cls,
        *,
        metadata: PromptMetadata,
        system_template: str,
        user_template: str,
        variables: tuple[PromptVariable, ...] = (),
    ) -> "PromptDefinition":

        if not system_template.strip():
            raise ValueError("System template cannot be empty")

        if not user_template.strip():
            raise ValueError("User template cannot be empty")

        return cls(
            metadata=metadata,
            system_template=system_template,
            user_template=user_template,
            variables=variables,
        )
