"""Tests for the V10 IntelligenceContext contract."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from uuid import UUID, uuid4

import pytest

from app.intelligence import IntelligenceContext
from app.summarization.intelligence import (
    DocumentProfile,
    DocumentStructureType,
    IntentClassification,
    SummarizationIntent,
)


def make_profile() -> DocumentProfile:
    return DocumentProfile(
        character_count=10,
        token_count=5,
        word_count=5,
        unique_word_count=4,
        paragraph_count=1,
        sentence_count=1,
        heading_count=0,
        list_item_count=0,
        code_block_count=0,
        quote_block_count=0,
        table_row_count=0,
        average_sentence_tokens=5.0,
        lexical_diversity=0.8,
        structure_type=DocumentStructureType.PROSE,
    )


def make_intent() -> IntentClassification:
    return IntentClassification(
        intent=SummarizationIntent.EXECUTIVE,
        confidence=1.0,
        scores={SummarizationIntent.EXECUTIVE: 1.0},
        explicit=True,
    )


def test_context_can_be_created_with_defaults() -> None:
    context = IntelligenceContext()

    assert isinstance(context.context_id, UUID)
    assert isinstance(context.correlation_id, UUID)
    assert context.request_id == ""
    assert context.document_profile is None
    assert context.intent_classification is None
    assert context.intent is None
    assert dict(context.constraints) == {}
    assert dict(context.metadata) == {}


def test_create_generates_context_id_and_preserves_correlation_id() -> None:
    correlation_id = uuid4()

    context = IntelligenceContext.create(
        request_id="request-123",
        correlation_id=correlation_id,
    )

    assert isinstance(context.context_id, UUID)
    assert context.correlation_id == correlation_id
    assert context.request_id == "request-123"


def test_context_composes_v93_document_and_intent_models() -> None:
    profile = make_profile()
    classification = make_intent()

    context = IntelligenceContext.create(
        document_profile=profile,
        intent_classification=classification,
    )

    assert context.document_profile is profile
    assert context.intent_classification is classification
    assert context.intent is SummarizationIntent.EXECUTIVE


def test_context_copies_constraints_and_metadata() -> None:
    constraints = {"max_tokens": 1000}
    metadata = {"source": "test"}

    context = IntelligenceContext.create(
        constraints=constraints,
        metadata=metadata,
    )

    constraints["max_tokens"] = 2000
    metadata["source"] = "changed"

    assert context.constraints["max_tokens"] == 1000
    assert context.metadata["source"] == "test"


def test_context_mappings_are_immutable() -> None:
    context = IntelligenceContext.create(
        constraints={"max_tokens": 1000},
        metadata={"source": "test"},
    )

    with pytest.raises(TypeError):
        context.constraints["max_tokens"] = 2000  # type: ignore[index]

    with pytest.raises(TypeError):
        context.metadata["source"] = "changed"  # type: ignore[index]


def test_context_is_frozen() -> None:
    context = IntelligenceContext()

    with pytest.raises(FrozenInstanceError):
        context.request_id = "changed"  # type: ignore[misc]


def test_context_rejects_invalid_context_id() -> None:
    with pytest.raises(TypeError, match="context_id must be a UUID"):
        IntelligenceContext(context_id="context")  # type: ignore[arg-type]


def test_context_rejects_invalid_request_id() -> None:
    with pytest.raises(TypeError, match="request_id must be a string"):
        IntelligenceContext(request_id=123)  # type: ignore[arg-type]


def test_context_rejects_invalid_correlation_id() -> None:
    with pytest.raises(TypeError, match="correlation_id must be a UUID"):
        IntelligenceContext(correlation_id="correlation")  # type: ignore[arg-type]


def test_context_rejects_invalid_document_profile() -> None:
    with pytest.raises(
        TypeError,
        match="document_profile must be a DocumentProfile or None",
    ):
        IntelligenceContext(document_profile=object())  # type: ignore[arg-type]


def test_context_rejects_invalid_intent_classification() -> None:
    with pytest.raises(
        TypeError,
        match="intent_classification must be an IntentClassification or None",
    ):
        IntelligenceContext(intent_classification=object())  # type: ignore[arg-type]


def test_context_rejects_non_mapping_constraints() -> None:
    with pytest.raises(TypeError, match="constraints must be a mapping"):
        IntelligenceContext(constraints=["invalid"])  # type: ignore[arg-type]


def test_context_rejects_non_mapping_metadata() -> None:
    with pytest.raises(TypeError, match="metadata must be a mapping"):
        IntelligenceContext(metadata=["invalid"])  # type: ignore[arg-type]


def test_context_is_provider_independent() -> None:
    context = IntelligenceContext.create(request_id="request-123")

    assert context.request_id == "request-123"
    assert not hasattr(context, "provider")
    assert not hasattr(context, "client")
