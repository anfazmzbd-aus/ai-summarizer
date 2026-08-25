"""
V10 M9 intelligence hardening integration and evaluation report.

Combines invariant, lifecycle scenario, and boundary stress evaluation
results into one immutable certification-style hardening report.

M9.6 performs aggregation only. It does not modify intelligence state,
repair failures, execute runtime behavior, or calculate scores.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .boundary_stress import BoundaryStressResult
from .intelligence_invariant import InvariantEvaluationResult
from .lifecycle_scenario_evaluator import LifecycleScenarioResult


class IntelligenceHardeningStatus(str, Enum):
    """Final V10 intelligence hardening status."""

    PASSED = "passed"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class IntelligenceHardeningReport:
    """Immutable integrated V10 intelligence hardening report."""

    status: IntelligenceHardeningStatus

    invariant_results: tuple[InvariantEvaluationResult, ...]
    scenario_results: tuple[LifecycleScenarioResult, ...]
    stress_results: tuple[BoundaryStressResult, ...]

    evaluated_invariants: int
    passed_invariants: int
    failed_invariants: int

    evaluated_scenarios: int
    passed_scenarios: int
    failed_scenarios: int

    evaluated_stress_cases: int
    passed_stress_cases: int
    failed_stress_cases: int

    reasons: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(
            self.status,
            IntelligenceHardeningStatus,
        ):
            raise TypeError("status must be an IntelligenceHardeningStatus")

        self._validate_result_tuple(
            field_name="invariant_results",
            values=self.invariant_results,
            expected_type=InvariantEvaluationResult,
        )

        self._validate_result_tuple(
            field_name="scenario_results",
            values=self.scenario_results,
            expected_type=LifecycleScenarioResult,
        )

        self._validate_result_tuple(
            field_name="stress_results",
            values=self.stress_results,
            expected_type=BoundaryStressResult,
        )

        count_fields = {
            "evaluated_invariants": self.evaluated_invariants,
            "passed_invariants": self.passed_invariants,
            "failed_invariants": self.failed_invariants,
            "evaluated_scenarios": self.evaluated_scenarios,
            "passed_scenarios": self.passed_scenarios,
            "failed_scenarios": self.failed_scenarios,
            "evaluated_stress_cases": self.evaluated_stress_cases,
            "passed_stress_cases": self.passed_stress_cases,
            "failed_stress_cases": self.failed_stress_cases,
        }

        for field_name, value in count_fields.items():
            if not isinstance(value, int) or isinstance(value, bool):
                raise TypeError(f"{field_name} must be an integer")

            if value < 0:
                raise ValueError(f"{field_name} must be greater than " "or equal to 0")

        if not isinstance(self.reasons, tuple):
            raise TypeError("reasons must be a tuple")

        for reason in self.reasons:
            if not isinstance(reason, str):
                raise TypeError("reasons must contain strings")

        self._validate_counts()
        self._validate_status()

    @staticmethod
    def _validate_result_tuple(
        *,
        field_name: str,
        values: tuple[object, ...],
        expected_type: type,
    ) -> None:
        if not isinstance(values, tuple):
            raise TypeError(f"{field_name} must be a tuple")

        for value in values:
            if not isinstance(value, expected_type):
                raise TypeError(
                    f"{field_name} must contain " f"{expected_type.__name__} values"
                )

    def _validate_counts(self) -> None:
        if self.evaluated_invariants != len(self.invariant_results):
            raise ValueError("evaluated_invariants must match " "invariant_results")

        if self.passed_invariants + self.failed_invariants != self.evaluated_invariants:
            raise ValueError(
                "invariant pass/fail counts must match " "evaluated_invariants"
            )

        if self.evaluated_scenarios != len(self.scenario_results):
            raise ValueError("evaluated_scenarios must match " "scenario_results")

        if self.passed_scenarios + self.failed_scenarios != self.evaluated_scenarios:
            raise ValueError(
                "scenario pass/fail counts must match " "evaluated_scenarios"
            )

        if self.evaluated_stress_cases != len(self.stress_results):
            raise ValueError("evaluated_stress_cases must match " "stress_results")

        if (
            self.passed_stress_cases + self.failed_stress_cases
            != self.evaluated_stress_cases
        ):
            raise ValueError(
                "stress pass/fail counts must match " "evaluated_stress_cases"
            )

    def _validate_status(self) -> None:
        any_failure = any(
            (
                self.failed_invariants > 0,
                self.failed_scenarios > 0,
                self.failed_stress_cases > 0,
            )
        )

        if self.status is IntelligenceHardeningStatus.PASSED and any_failure:
            raise ValueError("PASSED hardening status cannot contain failures")

        if self.status is IntelligenceHardeningStatus.FAILED and not any_failure:
            raise ValueError("FAILED hardening status requires at least one failure")


class IntelligenceHardeningReportBuilder:
    """Build the final integrated V10 intelligence hardening report."""

    def build(
        self,
        invariant_results: tuple[
            InvariantEvaluationResult,
            ...,
        ],
        scenario_results: tuple[
            LifecycleScenarioResult,
            ...,
        ],
        stress_results: tuple[
            BoundaryStressResult,
            ...,
        ],
    ) -> IntelligenceHardeningReport:
        """Aggregate all M9 hardening evidence."""

        self._validate_inputs(
            invariant_results=invariant_results,
            scenario_results=scenario_results,
            stress_results=stress_results,
        )

        passed_invariants = sum(result.passed for result in invariant_results)
        failed_invariants = len(invariant_results) - passed_invariants

        passed_scenarios = sum(result.passed for result in scenario_results)
        failed_scenarios = len(scenario_results) - passed_scenarios

        passed_stress_cases = sum(result.passed for result in stress_results)
        failed_stress_cases = len(stress_results) - passed_stress_cases

        has_failures = any(
            (
                failed_invariants,
                failed_scenarios,
                failed_stress_cases,
            )
        )

        status = (
            IntelligenceHardeningStatus.FAILED
            if has_failures
            else IntelligenceHardeningStatus.PASSED
        )

        reasons = self._build_reasons(
            failed_invariants=failed_invariants,
            failed_scenarios=failed_scenarios,
            failed_stress_cases=failed_stress_cases,
        )

        return IntelligenceHardeningReport(
            status=status,
            invariant_results=invariant_results,
            scenario_results=scenario_results,
            stress_results=stress_results,
            evaluated_invariants=len(invariant_results),
            passed_invariants=passed_invariants,
            failed_invariants=failed_invariants,
            evaluated_scenarios=len(scenario_results),
            passed_scenarios=passed_scenarios,
            failed_scenarios=failed_scenarios,
            evaluated_stress_cases=len(stress_results),
            passed_stress_cases=(passed_stress_cases),
            failed_stress_cases=(failed_stress_cases),
            reasons=reasons,
        )

    @staticmethod
    def _validate_inputs(
        *,
        invariant_results: tuple[
            InvariantEvaluationResult,
            ...,
        ],
        scenario_results: tuple[
            LifecycleScenarioResult,
            ...,
        ],
        stress_results: tuple[
            BoundaryStressResult,
            ...,
        ],
    ) -> None:
        checks = (
            (
                "invariant_results",
                invariant_results,
                InvariantEvaluationResult,
            ),
            (
                "scenario_results",
                scenario_results,
                LifecycleScenarioResult,
            ),
            (
                "stress_results",
                stress_results,
                BoundaryStressResult,
            ),
        )

        for field_name, values, expected_type in checks:
            if not isinstance(values, tuple):
                raise TypeError(f"{field_name} must be a tuple")

            for value in values:
                if not isinstance(value, expected_type):
                    raise TypeError(
                        f"{field_name} must contain " f"{expected_type.__name__} values"
                    )

    @staticmethod
    def _build_reasons(
        *,
        failed_invariants: int,
        failed_scenarios: int,
        failed_stress_cases: int,
    ) -> tuple[str, ...]:
        if not any(
            (
                failed_invariants,
                failed_scenarios,
                failed_stress_cases,
            )
        ):
            return (
                "all intelligence invariants passed",
                "all canonical lifecycle scenarios passed",
                "all boundary stress cases passed",
                "V10 intelligence hardening evaluation passed",
            )

        reasons: list[str] = []

        if failed_invariants:
            reasons.append(
                f"{failed_invariants} intelligence invariant " "evaluation(s) failed"
            )

        if failed_scenarios:
            reasons.append(
                f"{failed_scenarios} canonical lifecycle "
                "scenario evaluation(s) failed"
            )

        if failed_stress_cases:
            reasons.append(
                f"{failed_stress_cases} boundary stress " "evaluation(s) failed"
            )

        reasons.append("V10 intelligence hardening evaluation failed")

        return tuple(reasons)


__all__ = [
    "IntelligenceHardeningReport",
    "IntelligenceHardeningReportBuilder",
    "IntelligenceHardeningStatus",
]
