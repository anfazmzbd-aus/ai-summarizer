"""
V10 M10 release certification report.

Combines architecture certification, release integration scenario
evidence, compatibility evidence, and explicit release-validation gates
into one immutable V10 release-readiness result.

This module interprets supplied evidence only. It does not execute tests,
invoke Git, run pre-commit, call providers, modify runtime state, or
calculate readiness scores.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .architecture_certification import (
    V10ArchitectureCertification,
    V10ArchitectureCertificationStatus,
)
from .compatibility_boundary import (
    V10CompatibilityResult,
    V10CompatibilityStatus,
)
from .v10_integration_evaluator import (
    V10IntegrationScenarioResult,
)


class V10ReleaseReadinessStatus(str, Enum):
    """Final V10 release-readiness disposition."""

    READY = "ready"
    NOT_READY = "not_ready"


@dataclass(frozen=True, slots=True)
class V10ReleaseValidationEvidence:
    """
    Explicit externally-produced V10 release validation evidence.

    These fields record results produced by repository tooling.
    This contract does not execute that tooling itself.
    """

    intelligence_regression_passed: bool
    non_live_regression_passed: bool
    pre_commit_passed: bool
    diff_check_passed: bool
    documentation_complete: bool
    release_blockers_present: bool

    def __post_init__(self) -> None:
        boolean_fields = {
            "intelligence_regression_passed": (self.intelligence_regression_passed),
            "non_live_regression_passed": (self.non_live_regression_passed),
            "pre_commit_passed": self.pre_commit_passed,
            "diff_check_passed": self.diff_check_passed,
            "documentation_complete": (self.documentation_complete),
            "release_blockers_present": (self.release_blockers_present),
        }

        for field_name, value in boolean_fields.items():
            if not isinstance(value, bool):
                raise TypeError(f"{field_name} must be a bool")

    @property
    def passed(self) -> bool:
        """Return whether every external release validation gate passed."""

        return all(
            (
                self.intelligence_regression_passed,
                self.non_live_regression_passed,
                self.pre_commit_passed,
                self.diff_check_passed,
                self.documentation_complete,
                not self.release_blockers_present,
            )
        )


@dataclass(frozen=True, slots=True)
class V10ReleaseCertificationReport:
    """Immutable final V10 release certification result."""

    status: V10ReleaseReadinessStatus

    architecture_certification: V10ArchitectureCertification
    integration_results: tuple[
        V10IntegrationScenarioResult,
        ...,
    ]
    compatibility_result: V10CompatibilityResult
    validation_evidence: V10ReleaseValidationEvidence

    integration_scenarios_passed: bool

    reasons: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(
            self.status,
            V10ReleaseReadinessStatus,
        ):
            raise TypeError("status must be a V10ReleaseReadinessStatus")

        if not isinstance(
            self.architecture_certification,
            V10ArchitectureCertification,
        ):
            raise TypeError(
                "architecture_certification must be a " "V10ArchitectureCertification"
            )

        if not isinstance(
            self.integration_results,
            tuple,
        ):
            raise TypeError("integration_results must be a tuple")

        for result in self.integration_results:
            if not isinstance(
                result,
                V10IntegrationScenarioResult,
            ):
                raise TypeError(
                    "integration_results must contain "
                    "V10IntegrationScenarioResult values"
                )

        if not isinstance(
            self.compatibility_result,
            V10CompatibilityResult,
        ):
            raise TypeError("compatibility_result must be a " "V10CompatibilityResult")

        if not isinstance(
            self.validation_evidence,
            V10ReleaseValidationEvidence,
        ):
            raise TypeError(
                "validation_evidence must be a " "V10ReleaseValidationEvidence"
            )

        if not isinstance(
            self.integration_scenarios_passed,
            bool,
        ):
            raise TypeError("integration_scenarios_passed must be a bool")

        if not isinstance(self.reasons, tuple):
            raise TypeError("reasons must be a tuple")

        for reason in self.reasons:
            if not isinstance(reason, str):
                raise TypeError("reasons must contain strings")

        self._validate_integration_state()
        self._validate_status()

    def _validate_integration_state(self) -> None:
        actual_integration_pass = bool(self.integration_results) and all(
            result.passed for result in self.integration_results
        )

        if self.integration_scenarios_passed is not actual_integration_pass:
            raise ValueError(
                "integration_scenarios_passed must match " "integration_results"
            )

    def _validate_status(self) -> None:
        architecture_ok = (
            self.architecture_certification.status
            is V10ArchitectureCertificationStatus.CERTIFIED
        )

        compatibility_ok = (
            self.compatibility_result.status is V10CompatibilityStatus.COMPATIBLE
        )

        validation_ok = self.validation_evidence.passed

        all_requirements_passed = all(
            (
                architecture_ok,
                self.integration_scenarios_passed,
                compatibility_ok,
                validation_ok,
            )
        )

        if (
            self.status is V10ReleaseReadinessStatus.READY
            and not all_requirements_passed
        ):
            raise ValueError(
                "READY status requires all release " "requirements to pass"
            )

        if (
            self.status is V10ReleaseReadinessStatus.NOT_READY
            and all_requirements_passed
        ):
            raise ValueError(
                "NOT_READY status requires at least one " "release requirement to fail"
            )


class V10ReleaseCertificationReportBuilder:
    """Build the final deterministic V10 release certification report."""

    def build(
        self,
        *,
        architecture_certification: V10ArchitectureCertification,
        integration_results: tuple[
            V10IntegrationScenarioResult,
            ...,
        ],
        compatibility_result: V10CompatibilityResult,
        validation_evidence: V10ReleaseValidationEvidence,
    ) -> V10ReleaseCertificationReport:
        """Aggregate all V10 release-readiness evidence."""

        self._validate_inputs(
            architecture_certification=(architecture_certification),
            integration_results=integration_results,
            compatibility_result=compatibility_result,
            validation_evidence=validation_evidence,
        )

        architecture_ok = (
            architecture_certification.status
            is V10ArchitectureCertificationStatus.CERTIFIED
        )

        integration_ok = bool(integration_results) and all(
            result.passed for result in integration_results
        )

        compatibility_ok = (
            compatibility_result.status is V10CompatibilityStatus.COMPATIBLE
        )

        validation_ok = validation_evidence.passed

        ready = all(
            (
                architecture_ok,
                integration_ok,
                compatibility_ok,
                validation_ok,
            )
        )

        status = (
            V10ReleaseReadinessStatus.READY
            if ready
            else V10ReleaseReadinessStatus.NOT_READY
        )

        reasons = self._build_reasons(
            architecture_ok=architecture_ok,
            integration_ok=integration_ok,
            compatibility_ok=compatibility_ok,
            validation_evidence=validation_evidence,
        )

        return V10ReleaseCertificationReport(
            status=status,
            architecture_certification=(architecture_certification),
            integration_results=integration_results,
            compatibility_result=compatibility_result,
            validation_evidence=validation_evidence,
            integration_scenarios_passed=integration_ok,
            reasons=reasons,
        )

    @staticmethod
    def _validate_inputs(
        *,
        architecture_certification: V10ArchitectureCertification,
        integration_results: tuple[
            V10IntegrationScenarioResult,
            ...,
        ],
        compatibility_result: V10CompatibilityResult,
        validation_evidence: V10ReleaseValidationEvidence,
    ) -> None:
        if not isinstance(
            architecture_certification,
            V10ArchitectureCertification,
        ):
            raise TypeError(
                "architecture_certification must be a " "V10ArchitectureCertification"
            )

        if not isinstance(
            integration_results,
            tuple,
        ):
            raise TypeError("integration_results must be a tuple")

        for result in integration_results:
            if not isinstance(
                result,
                V10IntegrationScenarioResult,
            ):
                raise TypeError(
                    "integration_results must contain "
                    "V10IntegrationScenarioResult values"
                )

        if not isinstance(
            compatibility_result,
            V10CompatibilityResult,
        ):
            raise TypeError("compatibility_result must be a " "V10CompatibilityResult")

        if not isinstance(
            validation_evidence,
            V10ReleaseValidationEvidence,
        ):
            raise TypeError(
                "validation_evidence must be a " "V10ReleaseValidationEvidence"
            )

    @staticmethod
    def _build_reasons(
        *,
        architecture_ok: bool,
        integration_ok: bool,
        compatibility_ok: bool,
        validation_evidence: V10ReleaseValidationEvidence,
    ) -> tuple[str, ...]:
        reasons: list[str] = []

        if architecture_ok:
            reasons.append("V10 architecture certification passed")
        else:
            reasons.append("V10 architecture certification failed")

        if integration_ok:
            reasons.append("all supplied V10 integration scenarios passed")
        else:
            reasons.append(
                "V10 integration scenario certification failed "
                "or no integration evidence was supplied"
            )

        if compatibility_ok:
            reasons.append("V10 compatibility certification passed")
        else:
            reasons.append("V10 compatibility certification failed")

        if validation_evidence.intelligence_regression_passed:
            reasons.append("V10 intelligence regression passed")
        else:
            reasons.append("V10 intelligence regression failed")

        if validation_evidence.non_live_regression_passed:
            reasons.append("project non-live regression passed")
        else:
            reasons.append("project non-live regression failed")

        if validation_evidence.pre_commit_passed:
            reasons.append("pre-commit validation passed")
        else:
            reasons.append("pre-commit validation failed")

        if validation_evidence.diff_check_passed:
            reasons.append("git diff check passed")
        else:
            reasons.append("git diff check failed")

        if validation_evidence.documentation_complete:
            reasons.append("V10 release documentation is complete")
        else:
            reasons.append("V10 release documentation is incomplete")

        if validation_evidence.release_blockers_present:
            reasons.append("one or more V10 release blockers remain")
        else:
            reasons.append("no V10 release blockers are present")

        ready = all(
            (
                architecture_ok,
                integration_ok,
                compatibility_ok,
                validation_evidence.passed,
            )
        )

        reasons.append(
            "V10 release certification passed"
            if ready
            else "V10 release certification failed"
        )

        return tuple(reasons)


__all__ = [
    "V10ReleaseCertificationReport",
    "V10ReleaseCertificationReportBuilder",
    "V10ReleaseReadinessStatus",
    "V10ReleaseValidationEvidence",
]
