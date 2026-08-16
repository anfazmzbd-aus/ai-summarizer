"""Tests for V9.3-M3 deterministic intent-aware summarization."""

from __future__ import annotations

import pytest

from app.summarization.intelligence import (
    IntentClassification,
    IntentClassifier,
    SummarizationIntent,
)


def test_classifier_defaults_to_general_for_unmatched_text():
    result = IntentClassifier().classify("A short neutral document.")
    assert result.intent is SummarizationIntent.GENERAL
    assert result.confidence == 1.0
    assert result.explicit is False


def test_classifier_detects_action_items():
    result = IntentClassifier().classify("The team must follow up with the customer.")
    assert result.intent is SummarizationIntent.ACTION_ITEMS
    assert "must" in result.matched_terms
    assert "follow up" in result.matched_terms


def test_classifier_detects_technical_documents():
    result = IntentClassifier().classify(
        "The API deployment architecture and configuration changed."
    )
    assert result.intent is SummarizationIntent.TECHNICAL


def test_classifier_detects_findings():
    result = IntentClassifier().classify(
        "The research study reports new findings and evidence."
    )
    assert result.intent is SummarizationIntent.FINDINGS


def test_classifier_is_deterministic():
    text = "Market trends and recommendations for leadership."
    classifier = IntentClassifier()
    assert classifier.classify(text) == classifier.classify(text)


def test_explicit_intent_overrides_lexical_detection():
    result = IntentClassifier().classify(
        "The API deployment requires follow up.",
        intent=SummarizationIntent.EXECUTIVE,
    )
    assert result.intent is SummarizationIntent.EXECUTIVE
    assert result.confidence == 1.0
    assert result.explicit is True


def test_explicit_string_intent_is_supported():
    result = IntentClassifier().classify("content", intent="action_items")
    assert result.intent is SummarizationIntent.ACTION_ITEMS


def test_classifier_rejects_unknown_intent():
    with pytest.raises(ValueError, match="unsupported summarization intent"):
        IntentClassifier().classify("content", intent="unknown")


def test_classifier_rejects_invalid_input():
    with pytest.raises(TypeError, match="text must be a string"):
        IntentClassifier().classify(123)  # type: ignore[arg-type]


def test_classification_is_immutable():
    result = IntentClassifier().classify("content")
    with pytest.raises((AttributeError, TypeError)):
        result.intent = SummarizationIntent.TECHNICAL  # type: ignore[misc]


def test_classification_model_validation():
    with pytest.raises(ValueError, match="confidence"):
        IntentClassification(
            intent=SummarizationIntent.GENERAL,
            confidence=2.0,
            scores={},
        )
