"""
V10 M9 lifecycle scenario contracts.

Defines immutable canonical lifecycle evaluation scenarios used for
architecture hardening.

M9.3 defines scenario expectations only. It does not execute the
intelligence lifecycle or evaluate scenario outcomes.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .adaptation_decision import AdaptationDisposition
from .execution_integration import ExecutionIntegrationMode
from .observability_summary import IntelligenceObservabilityStatus
from .orchestration_directive import OrchestrationDisposition


class LifecycleScenarioKind(str, Enum):
    """Canonical V10 lifecycle scenario kinds."""

    NORMAL_PRESERVE = "normal_preserve"
    ADVISORY = "advisory"
    CONSTRAINED = "constrained"
    REVIEW = "review"
    NO_HISTORICAL_INFLUENCE = "no_historical_influence"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"


@dataclass(frozen=True, slots=True)
class LifecycleScenario:
    """
    Immutable expected lifecycle state for one canonical V10 scenario.
    """

    scenario_id: str
    kind: LifecycleScenarioKind
    name: str

    historical_influence_expected: bool
    adaptation_expected: bool

    expected_adaptation_disposition: AdaptationDisposition
    expected_orchestration_disposition: OrchestrationDisposition
    expected_integration_mode: ExecutionIntegrationMode
    expected_observability_status: IntelligenceObservabilityStatus

    execution_authorized_expected: bool
    review_required_expected: bool

    def __post_init__(self) -> None:
        if not isinstance(self.scenario_id, str):
            raise TypeError("scenario_id must be a string")

        if not self.scenario_id:
            raise ValueError("scenario_id must not be empty")

        if not isinstance(
            self.kind,
            LifecycleScenarioKind,
        ):
            raise TypeError("kind must be a LifecycleScenarioKind")

        if not isinstance(self.name, str):
            raise TypeError("name must be a string")

        if not self.name:
            raise ValueError("name must not be empty")

        boolean_fields = {
            "historical_influence_expected": (self.historical_influence_expected),
            "adaptation_expected": self.adaptation_expected,
            "execution_authorized_expected": (self.execution_authorized_expected),
            "review_required_expected": (self.review_required_expected),
        }

        for field_name, value in boolean_fields.items():
            if not isinstance(value, bool):
                raise TypeError(f"{field_name} must be a bool")

        if not isinstance(
            self.expected_adaptation_disposition,
            AdaptationDisposition,
        ):
            raise TypeError(
                "expected_adaptation_disposition must be an " "AdaptationDisposition"
            )

        if not isinstance(
            self.expected_orchestration_disposition,
            OrchestrationDisposition,
        ):
            raise TypeError(
                "expected_orchestration_disposition must be an "
                "OrchestrationDisposition"
            )

        if not isinstance(
            self.expected_integration_mode,
            ExecutionIntegrationMode,
        ):
            raise TypeError(
                "expected_integration_mode must be an " "ExecutionIntegrationMode"
            )

        if not isinstance(
            self.expected_observability_status,
            IntelligenceObservabilityStatus,
        ):
            raise TypeError(
                "expected_observability_status must be an "
                "IntelligenceObservabilityStatus"
            )


class CanonicalLifecycleScenarios:
    """Stable canonical V10 lifecycle scenario registry."""

    @staticmethod
    def all() -> tuple[LifecycleScenario, ...]:
        """Return the complete canonical lifecycle matrix."""

        return (
            LifecycleScenario(
                scenario_id="SCN-001",
                kind=LifecycleScenarioKind.NORMAL_PRESERVE,
                name="normal preserve lifecycle",
                historical_influence_expected=False,
                adaptation_expected=False,
                expected_adaptation_disposition=(AdaptationDisposition.PRESERVE),
                expected_orchestration_disposition=(OrchestrationDisposition.NO_CHANGE),
                expected_integration_mode=(ExecutionIntegrationMode.PRESERVE),
                expected_observability_status=(IntelligenceObservabilityStatus.NORMAL),
                execution_authorized_expected=False,
                review_required_expected=False,
            ),
            LifecycleScenario(
                scenario_id="SCN-002",
                kind=LifecycleScenarioKind.ADVISORY,
                name="advisory lifecycle",
                historical_influence_expected=True,
                adaptation_expected=True,
                expected_adaptation_disposition=(AdaptationDisposition.ADVISORY),
                expected_orchestration_disposition=(
                    OrchestrationDisposition.ADVISORY_CONTEXT
                ),
                expected_integration_mode=(ExecutionIntegrationMode.ADVISORY),
                expected_observability_status=(
                    IntelligenceObservabilityStatus.ADVISORY
                ),
                execution_authorized_expected=False,
                review_required_expected=False,
            ),
            LifecycleScenario(
                scenario_id="SCN-003",
                kind=LifecycleScenarioKind.CONSTRAINED,
                name="constrained lifecycle",
                historical_influence_expected=True,
                adaptation_expected=True,
                expected_adaptation_disposition=(AdaptationDisposition.CONSTRAIN),
                expected_orchestration_disposition=(
                    OrchestrationDisposition.BOUNDED_CONSTRAINT
                ),
                expected_integration_mode=(ExecutionIntegrationMode.CONSTRAINED),
                expected_observability_status=(
                    IntelligenceObservabilityStatus.CONSTRAINED
                ),
                execution_authorized_expected=True,
                review_required_expected=False,
            ),
            LifecycleScenario(
                scenario_id="SCN-004",
                kind=LifecycleScenarioKind.REVIEW,
                name="review lifecycle",
                historical_influence_expected=True,
                adaptation_expected=True,
                expected_adaptation_disposition=(AdaptationDisposition.REVIEW),
                expected_orchestration_disposition=(
                    OrchestrationDisposition.REVIEW_REQUIRED
                ),
                expected_integration_mode=(ExecutionIntegrationMode.REVIEW),
                expected_observability_status=(
                    IntelligenceObservabilityStatus.REVIEW_REQUIRED
                ),
                execution_authorized_expected=False,
                review_required_expected=True,
            ),
            LifecycleScenario(
                scenario_id="SCN-005",
                kind=(LifecycleScenarioKind.NO_HISTORICAL_INFLUENCE),
                name="no historical influence lifecycle",
                historical_influence_expected=False,
                adaptation_expected=False,
                expected_adaptation_disposition=(AdaptationDisposition.PRESERVE),
                expected_orchestration_disposition=(OrchestrationDisposition.NO_CHANGE),
                expected_integration_mode=(ExecutionIntegrationMode.PRESERVE),
                expected_observability_status=(IntelligenceObservabilityStatus.NORMAL),
                execution_authorized_expected=False,
                review_required_expected=False,
            ),
            LifecycleScenario(
                scenario_id="SCN-006",
                kind=(LifecycleScenarioKind.INSUFFICIENT_EVIDENCE),
                name="insufficient evidence lifecycle",
                historical_influence_expected=False,
                adaptation_expected=False,
                expected_adaptation_disposition=(AdaptationDisposition.PRESERVE),
                expected_orchestration_disposition=(OrchestrationDisposition.NO_CHANGE),
                expected_integration_mode=(ExecutionIntegrationMode.PRESERVE),
                expected_observability_status=(IntelligenceObservabilityStatus.NORMAL),
                execution_authorized_expected=False,
                review_required_expected=False,
            ),
        )

    @classmethod
    def get(
        cls,
        scenario_id: str,
    ) -> LifecycleScenario:
        """Return one canonical scenario by stable ID."""

        if not isinstance(scenario_id, str):
            raise TypeError("scenario_id must be a string")

        for scenario in cls.all():
            if scenario.scenario_id == scenario_id:
                return scenario

        raise ValueError(f"unknown lifecycle scenario: {scenario_id}")


__all__ = [
    "CanonicalLifecycleScenarios",
    "LifecycleScenario",
    "LifecycleScenarioKind",
]
