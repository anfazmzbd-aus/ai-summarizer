"""
V10 M10 architecture-wide certification.

Evaluates the immutable V10 capability manifest together with the M9
intelligence hardening report and produces a deterministic architecture
certification result.

This module does not execute runtime behavior, modify intelligence state,
repair failures, calculate scores, or provide execution authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .capability_manifest import (
    V10ArchitectureStatus,
    V10CapabilityManifest,
)
from .hardening_report import (
    IntelligenceHardeningReport,
    IntelligenceHardeningStatus,
)


class V10ArchitectureCertificationStatus(str, Enum):
    """Final architecture-certification disposition."""

    CERTIFIED = "certified"
    REJECTED = "rejected"


@dataclass(frozen=True, slots=True)
class V10ArchitectureCertification:
    """Immutable result of V10 architecture certification."""

    status: V10ArchitectureCertificationStatus
    version: str
    manifest_complete: bool
    feature_frozen: bool
    required_milestones_present: bool
    hardening_passed: bool
    reasons: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(
            self.status,
            V10ArchitectureCertificationStatus,
        ):
            raise TypeError("status must be a " "V10ArchitectureCertificationStatus")

        if not isinstance(self.version, str):
            raise TypeError("version must be a string")

        if self.version != "10.0.0":
            raise ValueError("version must be 10.0.0")

        bool_fields = {
            "manifest_complete": self.manifest_complete,
            "feature_frozen": self.feature_frozen,
            "required_milestones_present": (self.required_milestones_present),
            "hardening_passed": self.hardening_passed,
        }

        for field_name, value in bool_fields.items():
            if not isinstance(value, bool):
                raise TypeError(f"{field_name} must be a bool")

        if not isinstance(self.reasons, tuple):
            raise TypeError("reasons must be a tuple")

        for reason in self.reasons:
            if not isinstance(reason, str):
                raise TypeError("reasons must contain strings")

        all_requirements_passed = all(
            (
                self.manifest_complete,
                self.feature_frozen,
                self.required_milestones_present,
                self.hardening_passed,
            )
        )

        if (
            self.status is V10ArchitectureCertificationStatus.CERTIFIED
            and not all_requirements_passed
        ):
            raise ValueError(
                "CERTIFIED status requires all " "architecture requirements to pass"
            )

        if (
            self.status is V10ArchitectureCertificationStatus.REJECTED
            and all_requirements_passed
        ):
            raise ValueError(
                "REJECTED status requires at least one "
                "architecture requirement to fail"
            )


class V10ArchitectureCertificationEvaluator:
    """Evaluate V10 release architecture against canonical requirements."""

    REQUIRED_MILESTONES = (
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

    def evaluate(
        self,
        manifest: V10CapabilityManifest,
        hardening_report: IntelligenceHardeningReport,
    ) -> V10ArchitectureCertification:
        """Produce a deterministic architecture-certification result."""

        if not isinstance(
            manifest,
            V10CapabilityManifest,
        ):
            raise TypeError("manifest must be a V10CapabilityManifest")

        if not isinstance(
            hardening_report,
            IntelligenceHardeningReport,
        ):
            raise TypeError(
                "hardening_report must be an " "IntelligenceHardeningReport"
            )

        manifest_complete = (
            manifest.architecture_status is V10ArchitectureStatus.COMPLETE
        )

        feature_frozen = manifest.feature_frozen

        required_milestones_present = manifest.milestone_ids == self.REQUIRED_MILESTONES

        hardening_passed = hardening_report.status is IntelligenceHardeningStatus.PASSED

        requirements = (
            manifest_complete,
            feature_frozen,
            required_milestones_present,
            hardening_passed,
        )

        status = (
            V10ArchitectureCertificationStatus.CERTIFIED
            if all(requirements)
            else V10ArchitectureCertificationStatus.REJECTED
        )

        reasons = self._build_reasons(
            manifest_complete=manifest_complete,
            feature_frozen=feature_frozen,
            required_milestones_present=(required_milestones_present),
            hardening_passed=hardening_passed,
        )

        return V10ArchitectureCertification(
            status=status,
            version=manifest.version,
            manifest_complete=manifest_complete,
            feature_frozen=feature_frozen,
            required_milestones_present=(required_milestones_present),
            hardening_passed=hardening_passed,
            reasons=reasons,
        )

    @staticmethod
    def _build_reasons(
        *,
        manifest_complete: bool,
        feature_frozen: bool,
        required_milestones_present: bool,
        hardening_passed: bool,
    ) -> tuple[str, ...]:
        reasons: list[str] = []

        if manifest_complete:
            reasons.append("V10 architecture manifest is complete")
        else:
            reasons.append("V10 architecture manifest is incomplete")

        if feature_frozen:
            reasons.append("V10 architecture is feature frozen")
        else:
            reasons.append("V10 architecture is not feature frozen")

        if required_milestones_present:
            reasons.append("all required V10 M1-M9 milestones are present")
        else:
            reasons.append(
                "required V10 M1-M9 milestone set is incomplete "
                "or out of canonical order"
            )

        if hardening_passed:
            reasons.append("V10 intelligence hardening evaluation passed")
        else:
            reasons.append("V10 intelligence hardening evaluation failed")

        if all(
            (
                manifest_complete,
                feature_frozen,
                required_milestones_present,
                hardening_passed,
            )
        ):
            reasons.append("V10 architecture certification passed")
        else:
            reasons.append("V10 architecture certification rejected")

        return tuple(reasons)


__all__ = [
    "V10ArchitectureCertification",
    "V10ArchitectureCertificationEvaluator",
    "V10ArchitectureCertificationStatus",
]
