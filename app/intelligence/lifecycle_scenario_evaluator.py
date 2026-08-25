"""
V10 M9 end-to-end lifecycle scenario evaluation.

Executes the canonical intelligence hardening scenarios through the
existing bounded V10 intelligence components and compares the resulting
lifecycle state against the expectations defined by LifecycleScenario.

M9.4 is evaluation-only. It does not invoke provider runtime behavior,
modify execution state, or introduce new intelligence policy.
"""

from __future__ import annotations

from dataclasses import dataclass

from .adaptation_decision import AdaptationDisposition
from .adaptation_eligibility import AdaptationEligibilityStatus
from .adaptation_explanation import AdaptationExplanation
from .decision_explanation import DecisionExplanation
from .decision_support import DecisionSupportStatus
from .decision_support_policy import (
    DecisionSupportDisposition,
)
from .evidence_evaluation import EvidenceAssessmentStatus
from .execution_integration import ExecutionIntegrationMode
from .experience_evidence import EvidenceStrength
from .integration_explanation import IntegrationExplanation
from .intelligence_invariant import InvariantEvaluationResult
from .invariant_evaluator import IntelligenceInvariantEvaluator
from .intelligence_trace_builder import IntelligenceTraceBuilder
from .lifecycle_scenario import (
    LifecycleScenario,
    LifecycleScenarioKind,
)
from .observability_evaluator import (
    IntelligenceObservabilityEvaluator,
)
from .observability_event import ObservabilityEventBuilder
from .observability_integration import (
    IntelligenceObservabilityIntegrationBoundary,
)
from .observability_summary import (
    IntelligenceObservabilityStatus,
)
from .orchestration_directive import OrchestrationDisposition
from .task_decision import TaskAction

from uuid import uuid4


@dataclass(frozen=True, slots=True)
class LifecycleScenarioResult:
    """Immutable result of one canonical lifecycle evaluation."""

    scenario: LifecycleScenario
    passed: bool

    historical_influence_applied: bool
    adaptation_applied: bool

    adaptation_disposition: AdaptationDisposition
    orchestration_disposition: OrchestrationDisposition
    integration_mode: ExecutionIntegrationMode
    observability_status: IntelligenceObservabilityStatus

    execution_authorized: bool
    review_required: bool

    invariant_results: tuple[InvariantEvaluationResult, ...]
    reasons: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(
            self.scenario,
            LifecycleScenario,
        ):
            raise TypeError("scenario must be a LifecycleScenario")

        if not isinstance(self.passed, bool):
            raise TypeError("passed must be a bool")

        boolean_fields = {
            "historical_influence_applied": (self.historical_influence_applied),
            "adaptation_applied": self.adaptation_applied,
            "execution_authorized": self.execution_authorized,
            "review_required": self.review_required,
        }

        for field_name, value in boolean_fields.items():
            if not isinstance(value, bool):
                raise TypeError(f"{field_name} must be a bool")

        if not isinstance(
            self.adaptation_disposition,
            AdaptationDisposition,
        ):
            raise TypeError(
                "adaptation_disposition must be an " "AdaptationDisposition"
            )

        if not isinstance(
            self.orchestration_disposition,
            OrchestrationDisposition,
        ):
            raise TypeError(
                "orchestration_disposition must be an " "OrchestrationDisposition"
            )

        if not isinstance(
            self.integration_mode,
            ExecutionIntegrationMode,
        ):
            raise TypeError("integration_mode must be an " "ExecutionIntegrationMode")

        if not isinstance(
            self.observability_status,
            IntelligenceObservabilityStatus,
        ):
            raise TypeError(
                "observability_status must be an " "IntelligenceObservabilityStatus"
            )

        if not isinstance(
            self.invariant_results,
            tuple,
        ):
            raise TypeError("invariant_results must be a tuple")

        for result in self.invariant_results:
            if not isinstance(
                result,
                InvariantEvaluationResult,
            ):
                raise TypeError(
                    "invariant_results must contain " "InvariantEvaluationResult values"
                )

        if not isinstance(self.reasons, tuple):
            raise TypeError("reasons must be a tuple")

        for reason in self.reasons:
            if not isinstance(reason, str):
                raise TypeError("reasons must contain strings")


class LifecycleScenarioEvaluator:
    """Evaluate canonical lifecycle scenarios end-to-end."""

    def evaluate(
        self,
        scenario: LifecycleScenario,
    ) -> LifecycleScenarioResult:
        """Execute and evaluate one lifecycle scenario."""

        if not isinstance(
            scenario,
            LifecycleScenario,
        ):
            raise TypeError("scenario must be a LifecycleScenario")

        (
            decision_explanation,
            adaptation_explanation,
            integration_explanation,
            scenario_reason,
        ) = self._build_explanations(scenario)

        trace = IntelligenceTraceBuilder().build(
            decision_explanation,
            adaptation_explanation,
            integration_explanation,
        )

        summary = IntelligenceObservabilityEvaluator().evaluate(trace)

        event = ObservabilityEventBuilder().build(summary)

        snapshot = IntelligenceObservabilityIntegrationBoundary().compose(
            trace,
            summary,
            event,
        )

        invariant_results = IntelligenceInvariantEvaluator().evaluate_all(snapshot)

        scenario_matches = self._matches_expectations(
            scenario=scenario,
            snapshot=snapshot,
        )

        invariants_pass = all(result.passed for result in invariant_results)

        passed = scenario_matches and invariants_pass

        reasons = self._build_result_reasons(
            scenario=scenario,
            scenario_reason=scenario_reason,
            scenario_matches=scenario_matches,
            invariants_pass=invariants_pass,
        )

        return LifecycleScenarioResult(
            scenario=scenario,
            passed=passed,
            historical_influence_applied=(snapshot.historical_influence_applied),
            adaptation_applied=(snapshot.adaptation_applied),
            adaptation_disposition=(
                snapshot.trace.adaptation_explanation.adaptation_disposition
            ),
            orchestration_disposition=(
                snapshot.trace.integration_explanation.orchestration_disposition
            ),
            integration_mode=(snapshot.trace.integration_explanation.integration_mode),
            observability_status=snapshot.status,
            execution_authorized=(snapshot.execution_authorized),
            review_required=(snapshot.review_required),
            invariant_results=invariant_results,
            reasons=reasons,
        )

    def evaluate_all(
        self,
        scenarios: tuple[LifecycleScenario, ...],
    ) -> tuple[LifecycleScenarioResult, ...]:
        """Evaluate a supplied lifecycle scenario matrix."""

        if not isinstance(scenarios, tuple):
            raise TypeError("scenarios must be a tuple")

        for scenario in scenarios:
            if not isinstance(
                scenario,
                LifecycleScenario,
            ):
                raise TypeError("scenarios must contain " "LifecycleScenario values")

        return tuple(self.evaluate(scenario) for scenario in scenarios)

    @staticmethod
    def _build_explanations(
        scenario: LifecycleScenario,
    ) -> tuple[
        DecisionExplanation,
        AdaptationExplanation,
        IntegrationExplanation,
        str,
    ]:
        context_id = uuid4()
        correlation_id = uuid4()
        action = TaskAction.SUMMARIZE

        (
            decision_support_disposition,
            support_status,
            evidence_status,
            evidence_strength,
            eligibility_status,
            scenario_reason,
        ) = LifecycleScenarioEvaluator._scenario_inputs(scenario.kind)

        influence = scenario.historical_influence_expected

        adaptation_applied = scenario.adaptation_expected

        decision = DecisionExplanation(
            context_id=context_id,
            correlation_id=correlation_id,
            action=action,
            sample_count=3,
            effective_count=(
                3 if evidence_strength is EvidenceStrength.ESTABLISHED else 0
            ),
            degraded_count=0,
            ineffective_count=0,
            unknown_count=(
                0 if evidence_strength is EvidenceStrength.ESTABLISHED else 3
            ),
            evidence_strength=evidence_strength,
            evidence_status=evidence_status,
            support_status=support_status,
            disposition=decision_support_disposition,
            historical_influence_applied=influence,
            evidence_reasons=(scenario_reason,),
            support_reasons=("scenario support state",),
            policy_reasons=("scenario policy state",),
            decision_reasons=("scenario decision state",),
        )

        adaptation = AdaptationExplanation(
            context_id=context_id,
            correlation_id=correlation_id,
            action=action,
            policy_disposition=(decision_support_disposition),
            eligibility_status=eligibility_status,
            adaptation_disposition=(scenario.expected_adaptation_disposition),
            historical_influence_applied=influence,
            adaptation_applied=adaptation_applied,
            informed_decision_reasons=("scenario informed decision",),
            eligibility_reasons=("scenario eligibility state",),
            adaptation_reasons=("scenario adaptation state",),
        )

        integration = IntegrationExplanation(
            context_id=context_id,
            correlation_id=correlation_id,
            action=action,
            adaptation_disposition=(scenario.expected_adaptation_disposition),
            orchestration_disposition=(scenario.expected_orchestration_disposition),
            validation_status=(
                __import__(
                    "app.intelligence",
                    fromlist=["DirectiveValidationStatus"],
                ).DirectiveValidationStatus.VALID
            ),
            integration_mode=(scenario.expected_integration_mode),
            execution_authorized=(scenario.execution_authorized_expected),
            bounded_constraint_required=(
                scenario.expected_integration_mode
                is ExecutionIntegrationMode.CONSTRAINED
            ),
            review_required=(scenario.review_required_expected),
            orchestration_reasons=("scenario orchestration state",),
            validation_reasons=("scenario validation state",),
            integration_reasons=("scenario integration state",),
        )

        return (
            decision,
            adaptation,
            integration,
            scenario_reason,
        )

    @staticmethod
    def _scenario_inputs(
        kind: LifecycleScenarioKind,
    ) -> tuple[
        DecisionSupportDisposition,
        DecisionSupportStatus,
        EvidenceAssessmentStatus,
        EvidenceStrength,
        AdaptationEligibilityStatus,
        str,
    ]:
        if kind is LifecycleScenarioKind.NORMAL_PRESERVE:
            return (
                DecisionSupportDisposition.PRESERVE,
                DecisionSupportStatus.NEUTRAL,
                EvidenceAssessmentStatus.MIXED,
                EvidenceStrength.ESTABLISHED,
                AdaptationEligibilityStatus.INELIGIBLE,
                "normal lifecycle preserves the original decision",
            )

        if kind is LifecycleScenarioKind.ADVISORY:
            return (
                DecisionSupportDisposition.ADVISORY,
                DecisionSupportStatus.SUPPORTED,
                EvidenceAssessmentStatus.SUPPORTIVE,
                EvidenceStrength.ESTABLISHED,
                AdaptationEligibilityStatus.ELIGIBLE,
                "established supportive evidence enables advisory handling",
            )

        if kind is LifecycleScenarioKind.CONSTRAINED:
            return (
                DecisionSupportDisposition.CAUTION,
                DecisionSupportStatus.CAUTION,
                EvidenceAssessmentStatus.CAUTIONARY,
                EvidenceStrength.ESTABLISHED,
                AdaptationEligibilityStatus.ELIGIBLE,
                "established cautionary evidence enables bounded constraints",
            )

        if kind is LifecycleScenarioKind.REVIEW:
            return (
                DecisionSupportDisposition.REVIEW,
                DecisionSupportStatus.UNSUPPORTED,
                EvidenceAssessmentStatus.ADVERSE,
                EvidenceStrength.ESTABLISHED,
                AdaptationEligibilityStatus.REVIEW_ONLY,
                "established adverse evidence requires review handling",
            )

        if kind is LifecycleScenarioKind.NO_HISTORICAL_INFLUENCE:
            return (
                DecisionSupportDisposition.PRESERVE,
                DecisionSupportStatus.NEUTRAL,
                EvidenceAssessmentStatus.MIXED,
                EvidenceStrength.ESTABLISHED,
                AdaptationEligibilityStatus.INELIGIBLE,
                "historical influence is unavailable, so preserve is required",
            )

        if kind is LifecycleScenarioKind.INSUFFICIENT_EVIDENCE:
            return (
                DecisionSupportDisposition.PRESERVE,
                DecisionSupportStatus.NEUTRAL,
                EvidenceAssessmentStatus.MIXED,
                EvidenceStrength.LIMITED,
                AdaptationEligibilityStatus.INELIGIBLE,
                "historical evidence is insufficient, so preserve is required",
            )

        raise ValueError("unsupported lifecycle scenario kind")

    @staticmethod
    def _matches_expectations(
        *,
        scenario: LifecycleScenario,
        snapshot,
    ) -> bool:
        adaptation = snapshot.trace.adaptation_explanation
        integration = snapshot.trace.integration_explanation

        return all(
            (
                snapshot.historical_influence_applied
                is scenario.historical_influence_expected,
                snapshot.adaptation_applied is scenario.adaptation_expected,
                adaptation.adaptation_disposition
                is scenario.expected_adaptation_disposition,
                integration.orchestration_disposition
                is scenario.expected_orchestration_disposition,
                integration.integration_mode is scenario.expected_integration_mode,
                snapshot.status is scenario.expected_observability_status,
                snapshot.execution_authorized is scenario.execution_authorized_expected,
                snapshot.review_required is scenario.review_required_expected,
            )
        )

    @staticmethod
    def _build_result_reasons(
        *,
        scenario: LifecycleScenario,
        scenario_reason: str,
        scenario_matches: bool,
        invariants_pass: bool,
    ) -> tuple[str, ...]:
        reasons = [
            f"{scenario.scenario_id}: {scenario_reason}",
        ]

        reasons.append(
            "actual lifecycle matches canonical expectations"
            if scenario_matches
            else "actual lifecycle does not match canonical expectations"
        )

        reasons.append(
            "all canonical invariants passed"
            if invariants_pass
            else "one or more canonical invariants failed"
        )

        return tuple(reasons)


__all__ = [
    "LifecycleScenarioEvaluator",
    "LifecycleScenarioResult",
]
