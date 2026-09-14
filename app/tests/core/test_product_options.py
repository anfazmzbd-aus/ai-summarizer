from app.core.product_options import (
    SUMMARY_LENGTH_INSTRUCTIONS,
    SUMMARY_PROFILES,
    SummaryLength,
    SummaryType,
    resolve_length_instruction,
    resolve_summary_profile,
)
from app.summarization.intelligence import SummarizationIntent


def test_summary_type_values() -> None:
    assert SummaryType.GENERAL.value == "general"
    assert SummaryType.EXECUTIVE.value == "executive"
    assert SummaryType.KEY_POINTS.value == "key_points"
    assert SummaryType.ACTION_ITEMS.value == "action_items"
    assert SummaryType.FINDINGS.value == "findings"
    assert SummaryType.INSIGHTS.value == "insights"
    assert SummaryType.TECHNICAL.value == "technical"


def test_summary_length_values() -> None:
    assert SummaryLength.SHORT.value == "short"
    assert SummaryLength.MEDIUM.value == "medium"
    assert SummaryLength.DETAILED.value == "detailed"


def test_summary_profiles_cover_all_summary_types() -> None:
    assert set(SUMMARY_PROFILES) == set(SummaryType)


def test_summary_lengths_cover_all_length_values() -> None:
    assert set(SUMMARY_LENGTH_INSTRUCTIONS) == set(SummaryLength)


def test_general_maps_to_general_intent() -> None:
    profile = resolve_summary_profile(SummaryType.GENERAL)

    assert profile.intent is SummarizationIntent.GENERAL
    assert profile.instruction


def test_executive_maps_to_executive_intent() -> None:
    profile = resolve_summary_profile(SummaryType.EXECUTIVE)

    assert profile.intent is SummarizationIntent.EXECUTIVE


def test_key_points_maps_to_key_points_intent() -> None:
    profile = resolve_summary_profile(SummaryType.KEY_POINTS)

    assert profile.intent is SummarizationIntent.KEY_POINTS


def test_action_items_maps_to_action_items_intent() -> None:
    profile = resolve_summary_profile(SummaryType.ACTION_ITEMS)

    assert profile.intent is SummarizationIntent.ACTION_ITEMS


def test_findings_maps_to_findings_intent() -> None:
    profile = resolve_summary_profile(SummaryType.FINDINGS)

    assert profile.intent is SummarizationIntent.FINDINGS


def test_insights_maps_to_insights_intent() -> None:
    profile = resolve_summary_profile(SummaryType.INSIGHTS)

    assert profile.intent is SummarizationIntent.INSIGHTS


def test_technical_maps_to_technical_intent() -> None:
    profile = resolve_summary_profile(SummaryType.TECHNICAL)

    assert profile.intent is SummarizationIntent.TECHNICAL


def test_length_instructions_are_non_empty() -> None:
    for summary_length in SummaryLength:
        assert resolve_length_instruction(summary_length).strip()
