"""
V9.3-M3 deterministic intent classification for summarization.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping


class SummarizationIntent(str, Enum):
    """Supported high-level summarization intents."""

    GENERAL = "general"
    EXECUTIVE = "executive"
    ACTION_ITEMS = "action_items"
    KEY_POINTS = "key_points"
    FINDINGS = "findings"
    INSIGHTS = "insights"
    TECHNICAL = "technical"


@dataclass(frozen=True)
class IntentClassification:
    """Immutable deterministic result of intent classification."""

    intent: SummarizationIntent
    confidence: float
    scores: Mapping[SummarizationIntent, float]
    matched_terms: tuple[str, ...] = ()
    explicit: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.intent, SummarizationIntent):
            raise TypeError("intent must be a SummarizationIntent")
        if not 0 <= self.confidence <= 1:
            raise ValueError("confidence must be between zero and one")
        if not isinstance(self.scores, Mapping):
            raise TypeError("scores must be a mapping")
        if any(score < 0 for score in self.scores.values()):
            raise ValueError("intent scores must be non-negative")
        if not isinstance(self.matched_terms, tuple):
            raise TypeError("matched_terms must be a tuple")
        if not isinstance(self.metadata, dict):
            raise TypeError("metadata must be a dictionary")


class IntentClassifier:
    """Classify summarization intent without an LLM or external service.

    Explicit intent always wins. When intent is omitted, deterministic lexical
    signals provide a conservative classification and fall back to GENERAL.
    """

    classifier_version = "v9.3-m3"

    _TERMS: dict[SummarizationIntent, tuple[str, ...]] = {
        SummarizationIntent.EXECUTIVE: (
            "executive",
            "management",
            "leadership",
            "board",
            "decision maker",
            "business overview",
        ),
        SummarizationIntent.ACTION_ITEMS: (
            "action item",
            "action items",
            "follow up",
            "follow-up",
            "next step",
            "next steps",
            "should",
            "must",
            "need to",
            "todo",
            "to-do",
        ),
        SummarizationIntent.KEY_POINTS: (
            "key point",
            "key points",
            "highlights",
            "bullet points",
            "main points",
            "takeaways",
            "takeaways",
        ),
        SummarizationIntent.FINDINGS: (
            "findings",
            "research",
            "study",
            "results",
            "evidence",
            "observations",
        ),
        SummarizationIntent.INSIGHTS: (
            "insights",
            "implications",
            "trend",
            "trends",
            "drivers",
            "risks",
            "recommendations",
        ),
        SummarizationIntent.TECHNICAL: (
            "technical",
            "implementation",
            "architecture",
            "api",
            "code",
            "software",
            "configuration",
            "deployment",
            "stack trace",
        ),
    }

    def classify(
        self,
        text: str,
        *,
        intent: SummarizationIntent | str | None = None,
    ) -> IntentClassification:
        """Return a deterministic intent classification."""
        if not isinstance(text, str):
            raise TypeError("text must be a string")

        explicit = self._normalize_intent(intent)
        if explicit is not None:
            return IntentClassification(
                intent=explicit,
                confidence=1.0,
                scores={
                    candidate: float(candidate is explicit)
                    for candidate in SummarizationIntent
                },
                explicit=True,
                metadata={"classifier_version": self.classifier_version},
            )

        normalized = text.casefold()
        scores: dict[SummarizationIntent, float] = {
            candidate: 0.0 for candidate in SummarizationIntent
        }
        matches: dict[SummarizationIntent, list[str]] = {
            candidate: [] for candidate in SummarizationIntent
        }

        for candidate, terms in self._TERMS.items():
            for term in terms:
                if term in normalized:
                    scores[candidate] += 1.0
                    matches[candidate].append(term)

        best = max(
            scores,
            key=lambda candidate: (
                scores[candidate],
                -list(SummarizationIntent).index(candidate),
            ),
        )
        total = sum(scores.values())
        if total == 0:
            return IntentClassification(
                intent=SummarizationIntent.GENERAL,
                confidence=1.0,
                scores=scores,
                metadata={"classifier_version": self.classifier_version},
            )

        confidence = scores[best] / total
        return IntentClassification(
            intent=best,
            confidence=confidence,
            scores=scores,
            matched_terms=tuple(matches[best]),
            metadata={"classifier_version": self.classifier_version},
        )

    @staticmethod
    def _normalize_intent(
        intent: SummarizationIntent | str | None,
    ) -> SummarizationIntent | None:
        if intent is None:
            return None
        if isinstance(intent, SummarizationIntent):
            return intent
        if isinstance(intent, str):
            try:
                return SummarizationIntent(intent.casefold())
            except ValueError as exc:
                raise ValueError(f"unsupported summarization intent: {intent}") from exc
        raise TypeError("intent must be a SummarizationIntent, string, or None")
