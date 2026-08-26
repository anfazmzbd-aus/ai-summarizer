"""Tests for V10 M10 capability manifest and release contract."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from app.intelligence import (
    CanonicalV10CapabilityManifest,
    V10ArchitectureStatus,
    V10CapabilityManifest,
    V10MilestoneCapability,
)


def make_capability() -> V10MilestoneCapability:
    return V10MilestoneCapability(
        milestone_id="M1",
        name="Test Milestone",
        capabilities=(
            "capability one",
            "capability two",
        ),
    )


def make_manifest() -> V10CapabilityManifest:
    return V10CapabilityManifest(
        version="10.0.0",
        architecture_status=(V10ArchitectureStatus.COMPLETE),
        feature_frozen=True,
        milestones=(make_capability(),),
    )


def test_architecture_status_values_are_stable() -> None:
    assert V10ArchitectureStatus.COMPLETE.value == "complete"
    assert V10ArchitectureStatus.INCOMPLETE.value == "incomplete"


def test_milestone_capability_creation() -> None:
    result = make_capability()

    assert result.milestone_id == "M1"
    assert result.name == "Test Milestone"
    assert result.capabilities == (
        "capability one",
        "capability two",
    )


def test_milestone_id_requires_string() -> None:
    with pytest.raises(
        TypeError,
        match="milestone_id must be a string",
    ):
        V10MilestoneCapability(
            milestone_id=1,
            name="Test",
            capabilities=("capability",),
        )


def test_milestone_id_must_not_be_empty() -> None:
    with pytest.raises(
        ValueError,
        match="milestone_id must not be empty",
    ):
        V10MilestoneCapability(
            milestone_id="",
            name="Test",
            capabilities=("capability",),
        )


def test_name_requires_string() -> None:
    with pytest.raises(
        TypeError,
        match="name must be a string",
    ):
        V10MilestoneCapability(
            milestone_id="M1",
            name=1,
            capabilities=("capability",),
        )


def test_name_must_not_be_empty() -> None:
    with pytest.raises(
        ValueError,
        match="name must not be empty",
    ):
        V10MilestoneCapability(
            milestone_id="M1",
            name="",
            capabilities=("capability",),
        )


def test_capabilities_require_tuple() -> None:
    with pytest.raises(
        TypeError,
        match="capabilities must be a tuple",
    ):
        V10MilestoneCapability(
            milestone_id="M1",
            name="Test",
            capabilities=["capability"],
        )


def test_capabilities_must_not_be_empty() -> None:
    with pytest.raises(
        ValueError,
        match="capabilities must not be empty",
    ):
        V10MilestoneCapability(
            milestone_id="M1",
            name="Test",
            capabilities=(),
        )


def test_capabilities_require_strings() -> None:
    with pytest.raises(
        TypeError,
        match="capabilities must contain strings",
    ):
        V10MilestoneCapability(
            milestone_id="M1",
            name="Test",
            capabilities=("valid", 1),
        )


def test_capabilities_reject_empty_values() -> None:
    with pytest.raises(
        ValueError,
        match=("capabilities must not contain empty values"),
    ):
        V10MilestoneCapability(
            milestone_id="M1",
            name="Test",
            capabilities=("valid", ""),
        )


def test_manifest_creation() -> None:
    result = make_manifest()

    assert result.version == "10.0.0"
    assert result.architecture_status is V10ArchitectureStatus.COMPLETE
    assert result.feature_frozen is True


def test_manifest_requires_v10_version() -> None:
    with pytest.raises(
        ValueError,
        match="version must be 10.0.0",
    ):
        V10CapabilityManifest(
            version="11.0.0",
            architecture_status=(V10ArchitectureStatus.COMPLETE),
            feature_frozen=True,
            milestones=(make_capability(),),
        )


def test_manifest_version_requires_string() -> None:
    with pytest.raises(
        TypeError,
        match="version must be a string",
    ):
        V10CapabilityManifest(
            version=10,
            architecture_status=(V10ArchitectureStatus.COMPLETE),
            feature_frozen=True,
            milestones=(make_capability(),),
        )


def test_architecture_status_requires_enum() -> None:
    with pytest.raises(
        TypeError,
        match=("architecture_status must be a " "V10ArchitectureStatus"),
    ):
        V10CapabilityManifest(
            version="10.0.0",
            architecture_status="complete",
            feature_frozen=True,
            milestones=(make_capability(),),
        )


def test_feature_frozen_requires_bool() -> None:
    with pytest.raises(
        TypeError,
        match="feature_frozen must be a bool",
    ):
        V10CapabilityManifest(
            version="10.0.0",
            architecture_status=(V10ArchitectureStatus.COMPLETE),
            feature_frozen=1,
            milestones=(make_capability(),),
        )


def test_milestones_require_tuple() -> None:
    with pytest.raises(
        TypeError,
        match="milestones must be a tuple",
    ):
        V10CapabilityManifest(
            version="10.0.0",
            architecture_status=(V10ArchitectureStatus.COMPLETE),
            feature_frozen=True,
            milestones=[make_capability()],
        )


def test_milestones_require_capability_values() -> None:
    with pytest.raises(
        TypeError,
        match=("milestones must contain " "V10MilestoneCapability values"),
    ):
        V10CapabilityManifest(
            version="10.0.0",
            architecture_status=(V10ArchitectureStatus.COMPLETE),
            feature_frozen=True,
            milestones=("invalid",),
        )


def test_duplicate_milestone_ids_are_rejected() -> None:
    milestone = make_capability()

    with pytest.raises(
        ValueError,
        match="milestone IDs must be unique",
    ):
        V10CapabilityManifest(
            version="10.0.0",
            architecture_status=(V10ArchitectureStatus.COMPLETE),
            feature_frozen=True,
            milestones=(
                milestone,
                milestone,
            ),
        )


def test_manifest_milestone_ids_property() -> None:
    result = make_manifest()

    assert result.milestone_ids == ("M1",)


def test_manifest_capability_count_property() -> None:
    result = make_manifest()

    assert result.capability_count == 2


def test_capability_is_frozen() -> None:
    result = make_capability()

    with pytest.raises(FrozenInstanceError):
        result.name = "changed"


def test_manifest_is_frozen() -> None:
    result = make_manifest()

    with pytest.raises(FrozenInstanceError):
        result.feature_frozen = False


def test_capability_uses_slots() -> None:
    assert not hasattr(
        make_capability(),
        "__dict__",
    )


def test_manifest_uses_slots() -> None:
    assert not hasattr(
        make_manifest(),
        "__dict__",
    )


def test_canonical_manifest_version() -> None:
    manifest = CanonicalV10CapabilityManifest.build()

    assert manifest.version == "10.0.0"


def test_canonical_manifest_is_complete() -> None:
    manifest = CanonicalV10CapabilityManifest.build()

    assert manifest.architecture_status is V10ArchitectureStatus.COMPLETE


def test_canonical_manifest_is_feature_frozen() -> None:
    manifest = CanonicalV10CapabilityManifest.build()

    assert manifest.feature_frozen is True


def test_canonical_manifest_contains_m1_through_m9() -> None:
    manifest = CanonicalV10CapabilityManifest.build()

    assert manifest.milestone_ids == (
        "M1",
        "M2",
        "M3",
        "M4",
        "M5",
        "M6",
        "M7",
        "M8",
        "M9",
    )


def test_canonical_manifest_contains_nine_milestones() -> None:
    manifest = CanonicalV10CapabilityManifest.build()

    assert len(manifest.milestones) == 9


def test_every_canonical_milestone_has_capabilities() -> None:
    manifest = CanonicalV10CapabilityManifest.build()

    assert all(milestone.capabilities for milestone in manifest.milestones)


def test_canonical_manifest_is_deterministic() -> None:
    first = CanonicalV10CapabilityManifest.build()
    second = CanonicalV10CapabilityManifest.build()

    assert first == second


def test_canonical_capability_names_are_unique_per_milestone() -> None:
    manifest = CanonicalV10CapabilityManifest.build()

    for milestone in manifest.milestones:
        assert len(milestone.capabilities) == len(set(milestone.capabilities))


def test_manifest_contains_no_runtime_configuration() -> None:
    forbidden = {
        "provider",
        "model",
        "strategy",
        "retry",
        "timeout",
        "runtime",
        "executor",
        "execution_graph",
        "prompt",
        "streaming",
    }

    assert not (forbidden & set(V10CapabilityManifest.__dataclass_fields__))


def test_manifest_contains_no_scoring() -> None:
    forbidden = {
        "score",
        "percentage",
        "confidence",
        "probability",
        "quality_score",
        "risk_score",
    }

    assert not (forbidden & set(V10CapabilityManifest.__dataclass_fields__))


def test_canonical_factory_has_no_runtime_interface() -> None:
    forbidden = {
        "execute",
        "run",
        "retry",
        "replan",
        "adapt",
        "evaluate",
        "apply_runtime",
        "select_strategy",
        "switch_provider",
        "emit",
        "publish",
    }

    public_names = {
        name for name in dir(CanonicalV10CapabilityManifest) if not name.startswith("_")
    }

    assert not (forbidden & public_names)


def test_canonical_factory_exposes_only_build() -> None:
    public_names = {
        name for name in dir(CanonicalV10CapabilityManifest) if not name.startswith("_")
    }

    assert public_names == {"build"}
