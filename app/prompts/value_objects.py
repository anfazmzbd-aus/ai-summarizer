"""
AI Summarizer V9.0

Prompt domain value objects.

Defines strongly typed immutable identifiers
used throughout the prompt lifecycle.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PromptId:
    """
    Unique prompt identifier.
    """

    value: str

    def __post_init__(self) -> None:
        if not self.value.strip():
            raise ValueError("Prompt id cannot be empty")


@dataclass(frozen=True, slots=True)
class PromptVersion:
    """
    Semantic prompt version.
    """

    major: int
    minor: int
    patch: int

    def __post_init__(self) -> None:
        if self.major < 0 or self.minor < 0 or self.patch < 0:
            raise ValueError("Version values cannot be negative")

    def __str__(self) -> str:
        return f"{self.major}." f"{self.minor}." f"{self.patch}"


@dataclass(frozen=True, slots=True)
class PromptVariable:
    """
    Required template variable definition.
    """

    name: str

    description: str

    required: bool = True

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Variable name cannot be empty")
