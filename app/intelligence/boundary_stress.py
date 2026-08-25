"""
V10 M9 failure semantics and boundary stress evaluation.

Defines deterministic hardening cases that deliberately attempt invalid
state combinations against existing V10 intelligence boundaries.

M9.5 is evaluation-only. It does not repair invalid state, invoke runtime
behavior, alter policy, or create execution authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable


class BoundaryStressCategory(str, Enum):
    """Canonical hardening stress categories."""

    PROVENANCE = "provenance"
    AUTHORITY = "authority"
    STATE_CONSISTENCY = "state_consistency"
    HANDOFF = "handoff"
    OBSERVABILITY = "observability"
    TYPE_SAFETY = "type_safety"


@dataclass(frozen=True, slots=True)
class BoundaryStressCase:
    """Immutable definition of one adversarial hardening case."""

    case_id: str
    category: BoundaryStressCategory
    description: str

    def __post_init__(self) -> None:
        if not isinstance(self.case_id, str):
            raise TypeError("case_id must be a string")

        if not self.case_id:
            raise ValueError("case_id must not be empty")

        if not isinstance(
            self.category,
            BoundaryStressCategory,
        ):
            raise TypeError("category must be a BoundaryStressCategory")

        if not isinstance(self.description, str):
            raise TypeError("description must be a string")

        if not self.description:
            raise ValueError("description must not be empty")


@dataclass(frozen=True, slots=True)
class BoundaryStressResult:
    """Immutable result of one adversarial boundary stress case."""

    case: BoundaryStressCase
    passed: bool
    exception_type: str | None
    reasons: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(
            self.case,
            BoundaryStressCase,
        ):
            raise TypeError("case must be a BoundaryStressCase")

        if not isinstance(self.passed, bool):
            raise TypeError("passed must be a bool")

        if self.exception_type is not None and not isinstance(self.exception_type, str):
            raise TypeError("exception_type must be a string or None")

        if not isinstance(self.reasons, tuple):
            raise TypeError("reasons must be a tuple")

        for reason in self.reasons:
            if not isinstance(reason, str):
                raise TypeError("reasons must contain strings")


class BoundaryStressEvaluator:
    """Evaluate whether adversarial state fails closed as expected."""

    def evaluate(
        self,
        case: BoundaryStressCase,
        operation: Callable[[], object],
        expected_exception: type[Exception],
    ) -> BoundaryStressResult:
        """
        Execute one adversarial operation.

        The case passes only when the expected boundary exception is raised.
        """

        if not isinstance(case, BoundaryStressCase):
            raise TypeError("case must be a BoundaryStressCase")

        if not callable(operation):
            raise TypeError("operation must be callable")

        if not isinstance(expected_exception, type) or not issubclass(
            expected_exception,
            Exception,
        ):
            raise TypeError("expected_exception must be an Exception type")

        try:
            operation()
        except expected_exception as exc:
            return BoundaryStressResult(
                case=case,
                passed=True,
                exception_type=type(exc).__name__,
                reasons=(
                    "invalid architecture state was rejected "
                    "by the expected boundary",
                    str(exc),
                ),
            )
        except Exception as exc:
            return BoundaryStressResult(
                case=case,
                passed=False,
                exception_type=type(exc).__name__,
                reasons=(
                    "invalid architecture state was rejected "
                    "by an unexpected boundary exception",
                    str(exc),
                ),
            )

        return BoundaryStressResult(
            case=case,
            passed=False,
            exception_type=None,
            reasons=("invalid architecture state was accepted",),
        )

    def evaluate_all(
        self,
        cases: tuple[
            tuple[
                BoundaryStressCase,
                Callable[[], object],
                type[Exception],
            ],
            ...,
        ],
    ) -> tuple[BoundaryStressResult, ...]:
        """Evaluate a supplied adversarial case matrix."""

        if not isinstance(cases, tuple):
            raise TypeError("cases must be a tuple")

        results: list[BoundaryStressResult] = []

        for entry in cases:
            if not isinstance(entry, tuple) or len(entry) != 3:
                raise TypeError(
                    "cases must contain " "(case, operation, expected_exception) tuples"
                )

            case, operation, expected_exception = entry

            results.append(
                self.evaluate(
                    case,
                    operation,
                    expected_exception,
                )
            )

        return tuple(results)


__all__ = [
    "BoundaryStressCase",
    "BoundaryStressCategory",
    "BoundaryStressEvaluator",
    "BoundaryStressResult",
]
