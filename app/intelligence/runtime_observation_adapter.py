"""
V10 runtime observation adapter.

Translates existing runtime execution facts into the provider-independent
ExecutionObservation contract.

The adapter is intentionally one-way:

    Runtime state/result -> ExecutionObservation

It does not modify runtime state and does not expose runtime implementation
objects to the intelligence layer.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any
from uuid import UUID

from .execution_observation import ExecutionObservation, ExecutionOutcome


class RuntimeObservationAdapter:
    """Translate normalized runtime facts into an execution observation.

    The adapter operates on primitive/structural runtime facts rather than
    depending directly on ExecutionEngine or RuntimeManager. This keeps the
    intelligence layer decoupled from runtime implementation details.
    """

    def observe(
        self,
        *,
        execution_id: str,
        context_id: UUID,
        correlation_id: UUID,
        status: str,
        duration_ms: float = 0.0,
        retry_count: int = 0,
        fallback_used: bool = False,
        error: BaseException | str | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> ExecutionObservation:
        """Create an observation from normalized runtime execution facts."""

        return ExecutionObservation.create(
            execution_id=execution_id,
            context_id=context_id,
            correlation_id=correlation_id,
            outcome=self._map_outcome(status),
            duration_ms=duration_ms,
            retry_count=retry_count,
            fallback_used=fallback_used,
            error_type=self._error_type(error),
            error_message=self._error_message(error),
            metadata={} if metadata is None else metadata,
        )

    @staticmethod
    def _map_outcome(status: str) -> ExecutionOutcome:
        """Map runtime status values to normalized execution outcomes."""

        if not isinstance(status, str):
            raise TypeError("status must be a string")

        normalized = status.strip().lower()

        mapping = {
            "success": ExecutionOutcome.SUCCESS,
            "succeeded": ExecutionOutcome.SUCCESS,
            "completed": ExecutionOutcome.SUCCESS,
            "complete": ExecutionOutcome.SUCCESS,
            "failed": ExecutionOutcome.FAILED,
            "failure": ExecutionOutcome.FAILED,
            "cancelled": ExecutionOutcome.CANCELLED,
            "canceled": ExecutionOutcome.CANCELLED,
            "partial": ExecutionOutcome.PARTIAL,
        }

        try:
            return mapping[normalized]
        except KeyError as exc:
            raise ValueError(
                f"unsupported runtime execution status: {status!r}"
            ) from exc

    @staticmethod
    def _error_type(error: BaseException | str | None) -> str | None:
        """Normalize an error into its stable type name."""

        if error is None:
            return None

        if isinstance(error, BaseException):
            return type(error).__name__

        if isinstance(error, str):
            return "RuntimeError"

        raise TypeError("error must be an exception, string, or None")

    @staticmethod
    def _error_message(error: BaseException | str | None) -> str | None:
        """Normalize an error into a human-readable message."""

        if error is None:
            return None

        if isinstance(error, BaseException):
            return str(error)

        if isinstance(error, str):
            return error

        raise TypeError("error must be an exception, string, or None")

    @staticmethod
    def aggregate_retry_count(node_states: Sequence[Any]) -> int:
        """Aggregate retry counts from runtime node states.

        Runtime objects are inspected only at the adapter boundary. The
        resulting observation contains the numeric aggregate, not the
        runtime objects themselves.
        """

        total = 0

        for node_state in node_states:
            retry_count = getattr(node_state, "retries", 0)

            if not isinstance(retry_count, int) or isinstance(retry_count, bool):
                raise TypeError("runtime node retries must be integers")

            if retry_count < 0:
                raise ValueError("runtime node retries must be non-negative")

            total += retry_count

        return total


__all__ = ["RuntimeObservationAdapter"]
