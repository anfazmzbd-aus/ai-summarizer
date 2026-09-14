"""V13 product-level summarization options and policy mappings."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from app.summarization.intelligence import SummarizationIntent


class SummaryType(str, Enum):
    """Supported product-facing summary types."""

    GENERAL = "general"
    EXECUTIVE = "executive"
    KEY_POINTS = "key_points"
    ACTION_ITEMS = "action_items"
    FINDINGS = "findings"
    INSIGHTS = "insights"
    TECHNICAL = "technical"


class SummaryLength(str, Enum):
    """Supported product-facing summary lengths."""

    SHORT = "short"
    MEDIUM = "medium"
    DETAILED = "detailed"


@dataclass(frozen=True)
class SummaryProfile:
    """Resolved product semantics for a summary type."""

    intent: SummarizationIntent
    instruction: str


SUMMARY_PROFILES: dict[SummaryType, SummaryProfile] = {
    SummaryType.GENERAL: SummaryProfile(
        intent=SummarizationIntent.GENERAL,
        instruction="Provide a balanced summary of the important information.",
    ),
    SummaryType.EXECUTIVE: SummaryProfile(
        intent=SummarizationIntent.EXECUTIVE,
        instruction=(
            "Produce an executive-oriented summary emphasizing decisions, business "
            "implications, risks, outcomes, and information relevant to leadership."
        ),
    ),
    SummaryType.KEY_POINTS: SummaryProfile(
        intent=SummarizationIntent.KEY_POINTS,
        instruction="Present the principal points and takeaways clearly and directly.",
    ),
    SummaryType.ACTION_ITEMS: SummaryProfile(
        intent=SummarizationIntent.ACTION_ITEMS,
        instruction=(
            "Emphasize concrete actions, responsibilities, commitments, and next "
            "steps that are supported by the source."
        ),
    ),
    SummaryType.FINDINGS: SummaryProfile(
        intent=SummarizationIntent.FINDINGS,
        instruction=(
            "Emphasize findings, evidence, observations, and reported results from "
            "the source."
        ),
    ),
    SummaryType.INSIGHTS: SummaryProfile(
        intent=SummarizationIntent.INSIGHTS,
        instruction=(
            "Emphasize meaningful implications, patterns, trends, risks, and "
            "recommendations only when supported by the source."
        ),
    ),
    SummaryType.TECHNICAL: SummaryProfile(
        intent=SummarizationIntent.TECHNICAL,
        instruction=(
            "Preserve important technical concepts, architecture, implementation "
            "details, APIs, configuration, and engineering constraints."
        ),
    ),
}


SUMMARY_LENGTH_INSTRUCTIONS: dict[SummaryLength, str] = {
    SummaryLength.SHORT: (
        "Produce a concise summary containing only the most important information."
    ),
    SummaryLength.MEDIUM: (
        "Produce a balanced summary covering the principal information and important "
        "supporting context."
    ),
    SummaryLength.DETAILED: (
        "Produce a comprehensive summary preserving significant details, "
        "relationships, and supporting context while remaining a summary rather "
        "than reproducing the source."
    ),
}


def resolve_summary_profile(summary_type: SummaryType) -> SummaryProfile:
    """Return the authoritative product policy for a summary type."""

    return SUMMARY_PROFILES[summary_type]


def resolve_length_instruction(summary_length: SummaryLength) -> str:
    """Return the authoritative product policy for a summary length."""

    return SUMMARY_LENGTH_INSTRUCTIONS[summary_length]
