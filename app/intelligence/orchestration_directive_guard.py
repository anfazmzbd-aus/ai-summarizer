"""
V10 M7 orchestration directive guard boundary.

Validates translated orchestration directives before they can be handed
toward execution integration.

M7.3 performs authority validation only. It does not execute runtime
behavior, modify directives, select providers or strategies, or apply
orchestration changes.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .orchestration_directive import (
    OrchestrationDirective,
    OrchestrationDisposition,
)


class DirectiveValidationStatus(str, Enum):
    """Validation state for an orchestration directive."""

    VALID = "valid"
    REJECTED = "rejected"


@dataclass(frozen=True, slots=True)
class OrchestrationDirectiveValidation:
    """Immutable guard result for one orchestration directive."""

    directive: OrchestrationDirective
    status: DirectiveValidationStatus
    execution_authorized: bool
    review_required: bool
    reasons: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(
            self.directive,
            OrchestrationDirective,
        ):
            raise TypeError("directive must be an OrchestrationDirective")

        if not isinstance(
            self.status,
            DirectiveValidationStatus,
        ):
            raise TypeError("status must be a DirectiveValidationStatus")

        if not isinstance(
            self.execution_authorized,
            bool,
        ):
            raise TypeError("execution_authorized must be a bool")

        if not isinstance(
            self.review_required,
            bool,
        ):
            raise TypeError("review_required must be a bool")

        if not isinstance(self.reasons, tuple):
            raise TypeError("reasons must be a tuple")

        for reason in self.reasons:
            if not isinstance(reason, str):
                raise TypeError("reasons must contain strings")

        if (
            self.status is DirectiveValidationStatus.REJECTED
            and self.execution_authorized
        ):
            raise ValueError("rejected validation cannot authorize execution")


class OrchestrationDirectiveGuard:
    """Validate orchestration directives against bounded authority rules."""

    def validate(
        self,
        directive: OrchestrationDirective,
    ) -> OrchestrationDirectiveValidation:
        """Validate one orchestration directive deterministically."""

        if not isinstance(
            directive,
            OrchestrationDirective,
        ):
            raise TypeError("directive must be an OrchestrationDirective")

        valid, reason = self._validate_authority(directive)

        if not valid:
            return OrchestrationDirectiveValidation(
                directive=directive,
                status=DirectiveValidationStatus.REJECTED,
                execution_authorized=False,
                review_required=False,
                reasons=(
                    *directive.reasons,
                    reason,
                ),
            )

        execution_authorized = (
            directive.orchestration_disposition
            is OrchestrationDisposition.BOUNDED_CONSTRAINT
        )

        review_required = (
            directive.orchestration_disposition
            is OrchestrationDisposition.REVIEW_REQUIRED
        )

        return OrchestrationDirectiveValidation(
            directive=directive,
            status=DirectiveValidationStatus.VALID,
            execution_authorized=execution_authorized,
            review_required=review_required,
            reasons=(
                *directive.reasons,
                "orchestration directive passed bounded authority validation",
            ),
        )

    @staticmethod
    def _validate_authority(
        directive: OrchestrationDirective,
    ) -> tuple[bool, str]:
        disposition = directive.orchestration_disposition

        if disposition is OrchestrationDisposition.NO_CHANGE:
            if directive.execution_change_allowed:
                return (
                    False,
                    "NO_CHANGE cannot authorize execution changes",
                )

            if directive.review_required:
                return (
                    False,
                    "NO_CHANGE cannot require review",
                )

            return True, ""

        if disposition is OrchestrationDisposition.ADVISORY_CONTEXT:
            if directive.execution_change_allowed:
                return (
                    False,
                    "ADVISORY_CONTEXT cannot authorize execution changes",
                )

            if directive.review_required:
                return (
                    False,
                    "ADVISORY_CONTEXT cannot require review",
                )

            return True, ""

        if disposition is OrchestrationDisposition.BOUNDED_CONSTRAINT:
            if not directive.execution_change_allowed:
                return (
                    False,
                    "BOUNDED_CONSTRAINT requires execution change authority",
                )

            if directive.review_required:
                return (
                    False,
                    "BOUNDED_CONSTRAINT cannot require review",
                )

            return True, ""

        if disposition is OrchestrationDisposition.REVIEW_REQUIRED:
            if directive.execution_change_allowed:
                return (
                    False,
                    "REVIEW_REQUIRED cannot authorize execution changes",
                )

            if not directive.review_required:
                return (
                    False,
                    "REVIEW_REQUIRED requires review",
                )

            return True, ""

        return (
            False,
            "unsupported orchestration disposition",
        )


__all__ = [
    "DirectiveValidationStatus",
    "OrchestrationDirectiveGuard",
    "OrchestrationDirectiveValidation",
]
