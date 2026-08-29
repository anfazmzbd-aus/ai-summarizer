"""V11 application projection of post-execution V10 feedback."""

from __future__ import annotations

from time import perf_counter
from uuid import UUID, uuid4

from app.intelligence import (
    EvaluationCriteria,
    ExecutionEvaluator,
    ExecutionFeedbackBuilder,
    ExecutionObservation,
    ExecutionOutcome,
)


def build_execution_feedback_metadata(
    *,
    context_id: UUID,
    correlation_id: UUID,
    strategy: str,
    chunk_count: int,
    token_count: int,
    started_at: float,
) -> dict[str, str]:
    """Build descriptive metadata from one completed execution.

    The observation is created only after the canonical pipeline returns.
    Evaluation and feedback interpret those facts and cannot affect the
    already-completed execution or create a second control path.
    """

    observation = ExecutionObservation.create(
        execution_id=str(uuid4()),
        context_id=context_id,
        correlation_id=correlation_id,
        outcome=ExecutionOutcome.SUCCESS,
        duration_ms=(perf_counter() - started_at) * 1000,
        metadata={
            "strategy": strategy,
            "chunk_count": chunk_count,
            "token_count": token_count,
        },
    )
    evaluation = ExecutionEvaluator().evaluate(
        observation,
        EvaluationCriteria(),
    )
    feedback = ExecutionFeedbackBuilder().build(
        observation,
        evaluation,
    )

    return {
        "execution_id": observation.execution_id,
        "execution_outcome": observation.outcome.value,
        "execution_evaluation_status": evaluation.status.value,
        "execution_feedback_signals": ",".join(
            signal.value for signal in feedback.signals
        ),
    }


__all__ = ["build_execution_feedback_metadata"]
