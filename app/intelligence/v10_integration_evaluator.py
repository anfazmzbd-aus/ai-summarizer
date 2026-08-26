"""
V10 M10 release integration scenario evaluation.

Matches canonical V10 integration scenarios against existing M9
lifecycle, boundary-stress, and M10 architecture-certification evidence.

No runtime execution or policy mutation occurs here.
"""

from __future__ import annotations

from dataclasses import dataclass

from .architecture_certification import (
    V10ArchitectureCertification,
    V10ArchitectureCertificationStatus,
)
from .boundary_stress import BoundaryStressResult
from .lifecycle_scenario_evaluator import LifecycleScenarioResult
from .v10_integration_scenario import (
    V10IntegrationScenario,
    V10IntegrationScenarioKind,
)


@dataclass(frozen=True, slots=True)
class V10IntegrationScenarioResult:
    """Immutable result of one V10 release integration scenario."""

    scenario: V10IntegrationScenario
    passed: bool
    reasons: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(
            self.scenario,
            V10IntegrationScenario,
        ):
            raise TypeError("scenario must be a V10IntegrationScenario")

        if not isinstance(self.passed, bool):
            raise TypeError("passed must be a bool")

        if not isinstance(self.reasons, tuple):
            raise TypeError("reasons must be a tuple")

        for reason in self.reasons:
            if not isinstance(reason, str):
                raise TypeError("reasons must contain strings")


class V10IntegrationScenarioEvaluator:
    """Evaluate release scenarios from existing certification evidence."""

    def evaluate_lifecycle(
        self,
        scenario: V10IntegrationScenario,
        lifecycle_result: LifecycleScenarioResult,
    ) -> V10IntegrationScenarioResult:
        if not isinstance(
            scenario,
            V10IntegrationScenario,
        ):
            raise TypeError("scenario must be a V10IntegrationScenario")

        if not isinstance(
            lifecycle_result,
            LifecycleScenarioResult,
        ):
            raise TypeError("lifecycle_result must be a LifecycleScenarioResult")

        if scenario.kind in {
            V10IntegrationScenarioKind.REJECTED,
            V10IntegrationScenarioKind.CERTIFICATION,
        }:
            raise ValueError("scenario is not a lifecycle integration scenario")

        passed = (
            lifecycle_result.passed
            and lifecycle_result.execution_authorized == scenario.execution_authorized
            and lifecycle_result.review_required == scenario.review_required
        )

        return V10IntegrationScenarioResult(
            scenario=scenario,
            passed=passed == scenario.expected_pass,
            reasons=(
                (
                    "lifecycle integration expectation matched"
                    if passed == scenario.expected_pass
                    else "lifecycle integration expectation mismatched"
                ),
            ),
        )

    def evaluate_rejected(
        self,
        scenario: V10IntegrationScenario,
        stress_result: BoundaryStressResult,
    ) -> V10IntegrationScenarioResult:
        if not isinstance(
            scenario,
            V10IntegrationScenario,
        ):
            raise TypeError("scenario must be a V10IntegrationScenario")

        if scenario.kind is not V10IntegrationScenarioKind.REJECTED:
            raise ValueError("scenario must be a REJECTED integration scenario")

        if not isinstance(
            stress_result,
            BoundaryStressResult,
        ):
            raise TypeError("stress_result must be a BoundaryStressResult")

        matched = stress_result.passed

        return V10IntegrationScenarioResult(
            scenario=scenario,
            passed=matched == scenario.expected_pass,
            reasons=(
                (
                    "rejected orchestration failed closed"
                    if matched
                    else "rejected orchestration did not fail closed"
                ),
            ),
        )

    def evaluate_certification(
        self,
        scenario: V10IntegrationScenario,
        certification: V10ArchitectureCertification,
    ) -> V10IntegrationScenarioResult:
        if not isinstance(
            scenario,
            V10IntegrationScenario,
        ):
            raise TypeError("scenario must be a V10IntegrationScenario")

        if scenario.kind is not V10IntegrationScenarioKind.CERTIFICATION:
            raise ValueError("scenario must be a CERTIFICATION " "integration scenario")

        if not isinstance(
            certification,
            V10ArchitectureCertification,
        ):
            raise TypeError("certification must be a " "V10ArchitectureCertification")

        matched = certification.status is V10ArchitectureCertificationStatus.CERTIFIED

        return V10IntegrationScenarioResult(
            scenario=scenario,
            passed=matched == scenario.expected_pass,
            reasons=(
                (
                    "architecture certification expectation matched"
                    if matched == scenario.expected_pass
                    else "architecture certification expectation mismatched"
                ),
            ),
        )


__all__ = [
    "V10IntegrationScenarioEvaluator",
    "V10IntegrationScenarioResult",
]
