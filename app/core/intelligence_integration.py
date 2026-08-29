"""V11 application boundary for the existing V10 intelligence lifecycle."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID, uuid4

from app.intelligence import (
    AdaptationEligibilityEvaluator,
    AdaptationExplanationBuilder,
    AdaptiveIntelligencePolicy,
    AdaptivePolicyCompositionBoundary,
    DecisionSupportDisposition,
    DecisionSupportPolicyResult,
    DecisionSupportStatus,
    DirectiveValidationStatus,
    EvidenceAssessmentStatus,
    EvidenceStrength,
    ExperienceInformedDecisionBoundary,
    ExistingExecutionIntegrationAdapter,
    IntelligenceContext,
    IntelligenceOrchestrationHandoff,
    IntelligenceOrchestrationHandoffBoundary,
    IntelligenceOrchestrator,
    OrchestrationDirectiveGuard,
    OrchestrationTranslationPolicy,
)
from .application_contracts import SummarizationApplicationRequest


@dataclass(frozen=True, slots=True)
class ApplicationIntelligenceResult:
    """Application-owned projection of a validated V10 handoff.

    V10 contracts do not cross the application result boundary.  The
    projection is descriptive and cannot authorize or apply execution changes.
    """

    context_id: UUID
    correlation_id: UUID
    action: str
    mode: str
    execution_change_authorized: bool
    bounded_constraint_required: bool
    review_required: bool
    reasons: tuple[str, ...]
    trace_id: str
    explainability_summary: str
    observability_status: str
    diagnostic_code: str
    diagnostic_message: str
    reason_count: int


class ApplicationIntelligenceBoundary:
    """Translate canonical application context through existing V10 policy.

    M3.1 intentionally supplies no historical evidence or execution
    constraints, so the V10 lifecycle resolves to PRESERVE.  The application
    receives only the validated projection below.  M3.3 carries the existing
    V10 bounded-constraint decision across this boundary without exposing V10
    contracts or applying provider/runtime changes.
    """

    def evaluate(
        self,
        request: SummarizationApplicationRequest,
    ) -> ApplicationIntelligenceResult:
        """Return execution-neutral V10 guidance for one application request."""
        if not isinstance(request, SummarizationApplicationRequest):
            raise TypeError("request must be a SummarizationApplicationRequest")

        context = IntelligenceContext.create(
            request_id=str(uuid4()),
            metadata={
                "source": "canonical_application",
                "text_length": str(len(request.text)),
                "has_prompt_name": str(request.prompt_name is not None),
            },
        )
        decision = IntelligenceOrchestrator().decide(context)

        policy_result = DecisionSupportPolicyResult.create(
            context_id=context.context_id,
            correlation_id=context.correlation_id,
            action=decision.action,
            support_status=DecisionSupportStatus.NEUTRAL,
            evidence_status=EvidenceAssessmentStatus.MIXED,
            evidence_strength=EvidenceStrength.ESTABLISHED,
            disposition=DecisionSupportDisposition.PRESERVE,
            reasons=("canonical application supplies no historical directive",),
        )
        informed = ExperienceInformedDecisionBoundary().compose(
            decision,
            policy_result,
        )
        eligibility = AdaptationEligibilityEvaluator().evaluate(informed)
        adaptation = AdaptiveIntelligencePolicy().apply(informed, eligibility)
        explanation = AdaptationExplanationBuilder().build(
            informed,
            eligibility,
            adaptation,
        )
        outcome = AdaptivePolicyCompositionBoundary().compose(
            informed,
            eligibility,
            adaptation,
            explanation,
        )
        directive = OrchestrationTranslationPolicy().translate(outcome)
        validation = OrchestrationDirectiveGuard().validate(directive)
        handoff = IntelligenceOrchestrationHandoffBoundary().compose(
            outcome,
            directive,
            validation,
        )

        return self._project_validated_handoff(handoff)

    @staticmethod
    def _project_validated_handoff(
        handoff: IntelligenceOrchestrationHandoff,
    ) -> ApplicationIntelligenceResult:
        if handoff.validation.status is not DirectiveValidationStatus.VALID:
            raise ValueError("V10 handoff must have valid directive validation")

        integration = ExistingExecutionIntegrationAdapter().adapt(handoff)
        mode = integration.mode.value
        observability = {
            "preserve": (
                "normal",
                "INTELLIGENCE_NORMAL",
                "intelligence lifecycle completed with normal execution-preserving behavior",
            ),
            "advisory": (
                "advisory",
                "INTELLIGENCE_ADVISORY",
                "intelligence lifecycle includes advisory historical context",
            ),
            "constrained": (
                "constrained",
                "INTELLIGENCE_CONSTRAINED",
                "intelligence lifecycle requires approved bounded execution constraints",
            ),
            "review": (
                "review_required",
                "INTELLIGENCE_REVIEW_REQUIRED",
                "intelligence lifecycle requires review-oriented handling",
            ),
        }
        observability_status, diagnostic_code, diagnostic_message = observability[mode]
        reasons = integration.reasons
        return ApplicationIntelligenceResult(
            context_id=integration.context_id,
            correlation_id=integration.correlation_id,
            action=integration.action.value,
            mode=integration.mode.value,
            execution_change_authorized=integration.execution_change_authorized,
            bounded_constraint_required=integration.bounded_constraint_required,
            review_required=integration.review_required,
            reasons=reasons,
            trace_id=str(integration.context_id),
            explainability_summary="; ".join(reasons),
            observability_status=observability_status,
            diagnostic_code=diagnostic_code,
            diagnostic_message=diagnostic_message,
            reason_count=len(reasons),
        )


__all__ = [
    "ApplicationIntelligenceBoundary",
    "ApplicationIntelligenceResult",
]
