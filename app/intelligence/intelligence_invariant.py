"""
V10 M9 intelligence invariant contracts.

Defines immutable architecture-hardening contracts representing V10
intelligence invariants and their evaluation results.

M9.1 defines representation only. It does not evaluate invariants,
execute runtime behavior, alter intelligence state, or produce a
hardening certification result.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class IntelligenceInvariantCategory(str, Enum):
    """Architecture-hardening invariant categories."""

    PROVENANCE = "provenance"
    AUTHORITY = "authority"
    STATE_CONSISTENCY = "state_consistency"
    IMMUTABILITY = "immutability"
    DETERMINISM = "determinism"
    RUNTIME_ISOLATION = "runtime_isolation"


class IntelligenceInvariantSeverity(str, Enum):
    """Importance of an intelligence architecture invariant."""

    REQUIRED = "required"
    CRITICAL = "critical"


@dataclass(frozen=True, slots=True)
class IntelligenceInvariant:
    """
    Immutable definition of one V10 intelligence architecture invariant.

    The contract describes what must remain true. It contains no
    evaluation logic.
    """

    invariant_id: str
    category: IntelligenceInvariantCategory
    severity: IntelligenceInvariantSeverity
    description: str

    def __post_init__(self) -> None:
        if not isinstance(self.invariant_id, str):
            raise TypeError("invariant_id must be a string")

        if not self.invariant_id:
            raise ValueError("invariant_id must not be empty")

        if not isinstance(
            self.category,
            IntelligenceInvariantCategory,
        ):
            raise TypeError("category must be an " "IntelligenceInvariantCategory")

        if not isinstance(
            self.severity,
            IntelligenceInvariantSeverity,
        ):
            raise TypeError("severity must be an " "IntelligenceInvariantSeverity")

        if not isinstance(self.description, str):
            raise TypeError("description must be a string")

        if not self.description:
            raise ValueError("description must not be empty")

    @classmethod
    def create(
        cls,
        *,
        invariant_id: str,
        category: IntelligenceInvariantCategory,
        severity: IntelligenceInvariantSeverity,
        description: str,
    ) -> "IntelligenceInvariant":
        """Create an immutable intelligence invariant."""

        return cls(
            invariant_id=invariant_id,
            category=category,
            severity=severity,
            description=description,
        )


@dataclass(frozen=True, slots=True)
class InvariantEvaluationResult:
    """
    Immutable evaluation result for one intelligence invariant.

    M9.1 defines this representation only. M9.2 will own invariant
    evaluation behavior.
    """

    invariant: IntelligenceInvariant
    passed: bool
    reasons: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(
            self.invariant,
            IntelligenceInvariant,
        ):
            raise TypeError("invariant must be an IntelligenceInvariant")

        if not isinstance(self.passed, bool):
            raise TypeError("passed must be a bool")

        if not isinstance(self.reasons, tuple):
            raise TypeError("reasons must be a tuple")

        for reason in self.reasons:
            if not isinstance(reason, str):
                raise TypeError("reasons must contain strings")

    @classmethod
    def create(
        cls,
        *,
        invariant: IntelligenceInvariant,
        passed: bool,
        reasons: tuple[str, ...],
    ) -> "InvariantEvaluationResult":
        """Create an immutable invariant evaluation result."""

        return cls(
            invariant=invariant,
            passed=passed,
            reasons=reasons,
        )


__all__ = [
    "IntelligenceInvariant",
    "IntelligenceInvariantCategory",
    "IntelligenceInvariantSeverity",
    "InvariantEvaluationResult",
]
