"""
V10 intelligence context contract.

The intelligence context is an immutable, provider-independent snapshot of the
information available to an orchestration decision.  It composes existing
V9.3 document and intent intelligence without owning their implementations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping
from uuid import UUID, uuid4

from app.summarization.intelligence import DocumentProfile, IntentClassification


@dataclass(frozen=True, slots=True)
class IntelligenceContext:
    """Immutable context supplied to V10 intelligence decisions.

    The context deliberately does not contain source text, provider clients,
    runtime objects, or executable behavior.  Source processing remains owned
    by the V9.3 summarization domain, while this object provides a stable
    orchestration-level boundary around its derived intelligence.
    """

    context_id: UUID = field(default_factory=uuid4)
    request_id: str = ""
    correlation_id: UUID = field(default_factory=uuid4)
    document_profile: DocumentProfile | None = None
    intent_classification: IntentClassification | None = None
    constraints: Mapping[str, Any] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.context_id, UUID):
            raise TypeError("context_id must be a UUID")

        if not isinstance(self.request_id, str):
            raise TypeError("request_id must be a string")

        if not isinstance(self.correlation_id, UUID):
            raise TypeError("correlation_id must be a UUID")

        if self.document_profile is not None and not isinstance(
            self.document_profile, DocumentProfile
        ):
            raise TypeError("document_profile must be a DocumentProfile or None")

        if self.intent_classification is not None and not isinstance(
            self.intent_classification, IntentClassification
        ):
            raise TypeError(
                "intent_classification must be an IntentClassification or None"
            )

        if not isinstance(self.constraints, Mapping):
            raise TypeError("constraints must be a mapping")

        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")

        object.__setattr__(
            self, "constraints", MappingProxyType(dict(self.constraints))
        )
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    @property
    def intent(self):
        """Return the classified intent when one is available."""
        if self.intent_classification is None:
            return None
        return self.intent_classification.intent

    @classmethod
    def create(
        cls,
        *,
        request_id: str = "",
        correlation_id: UUID | None = None,
        document_profile: DocumentProfile | None = None,
        intent_classification: IntentClassification | None = None,
        constraints: Mapping[str, Any] | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> "IntelligenceContext":
        """Create a context with generated identifiers."""
        return cls(
            request_id=request_id,
            correlation_id=correlation_id or uuid4(),
            document_profile=document_profile,
            intent_classification=intent_classification,
            constraints={} if constraints is None else constraints,
            metadata={} if metadata is None else metadata,
        )


__all__ = ["IntelligenceContext"]
