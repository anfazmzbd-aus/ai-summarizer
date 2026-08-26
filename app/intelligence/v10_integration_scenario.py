"""
V10 M10 release-level integration scenario matrix.

Defines canonical integration expectations used to certify that the
bounded-intelligence architecture remains coherent at the V10 release
boundary.

The scenarios are declarative only. They do not execute runtime behavior
or provide execution authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class V10IntegrationScenarioKind(str, Enum):
    """Canonical V10 integration scenario categories."""

    PRESERVE = "preserve"
    ADVISORY = "advisory"
    CONSTRAINED = "constrained"
    REVIEW = "review"
    REJECTED = "rejected"
    CERTIFICATION = "certification"


@dataclass(frozen=True, slots=True)
class V10IntegrationScenario:
    """Immutable expected outcome for one V10 release scenario."""

    scenario_id: str
    name: str
    kind: V10IntegrationScenarioKind
    execution_authorized: bool
    review_required: bool
    expected_pass: bool

    def __post_init__(self) -> None:
        if not isinstance(self.scenario_id, str):
            raise TypeError("scenario_id must be a string")

        if not self.scenario_id:
            raise ValueError("scenario_id must not be empty")

        if not isinstance(self.name, str):
            raise TypeError("name must be a string")

        if not self.name:
            raise ValueError("name must not be empty")

        if not isinstance(
            self.kind,
            V10IntegrationScenarioKind,
        ):
            raise TypeError("kind must be a V10IntegrationScenarioKind")

        if not isinstance(
            self.execution_authorized,
            bool,
        ):
            raise TypeError("execution_authorized must be a bool")

        if not isinstance(self.review_required, bool):
            raise TypeError("review_required must be a bool")

        if not isinstance(self.expected_pass, bool):
            raise TypeError("expected_pass must be a bool")

        if (
            self.kind is not V10IntegrationScenarioKind.CONSTRAINED
            and self.execution_authorized
        ):
            raise ValueError("only CONSTRAINED scenarios may authorize execution")

        if (
            self.kind is V10IntegrationScenarioKind.CONSTRAINED
            and not self.execution_authorized
        ):
            raise ValueError("CONSTRAINED scenarios require execution authority")

        if self.kind is V10IntegrationScenarioKind.REVIEW and not self.review_required:
            raise ValueError("REVIEW scenarios require review")

        if self.kind is not V10IntegrationScenarioKind.REVIEW and self.review_required:
            raise ValueError("only REVIEW scenarios may require review")


class CanonicalV10IntegrationScenarios:
    """Factory for the canonical V10 release integration matrix."""

    @staticmethod
    def all() -> tuple[V10IntegrationScenario, ...]:
        return (
            V10IntegrationScenario(
                scenario_id="V10-INT-001",
                name="normal preserve",
                kind=V10IntegrationScenarioKind.PRESERVE,
                execution_authorized=False,
                review_required=False,
                expected_pass=True,
            ),
            V10IntegrationScenario(
                scenario_id="V10-INT-002",
                name="no historical influence",
                kind=V10IntegrationScenarioKind.PRESERVE,
                execution_authorized=False,
                review_required=False,
                expected_pass=True,
            ),
            V10IntegrationScenario(
                scenario_id="V10-INT-003",
                name="advisory lifecycle",
                kind=V10IntegrationScenarioKind.ADVISORY,
                execution_authorized=False,
                review_required=False,
                expected_pass=True,
            ),
            V10IntegrationScenario(
                scenario_id="V10-INT-004",
                name="constrained lifecycle",
                kind=V10IntegrationScenarioKind.CONSTRAINED,
                execution_authorized=True,
                review_required=False,
                expected_pass=True,
            ),
            V10IntegrationScenario(
                scenario_id="V10-INT-005",
                name="review lifecycle",
                kind=V10IntegrationScenarioKind.REVIEW,
                execution_authorized=False,
                review_required=True,
                expected_pass=True,
            ),
            V10IntegrationScenario(
                scenario_id="V10-INT-006",
                name="insufficient evidence",
                kind=V10IntegrationScenarioKind.PRESERVE,
                execution_authorized=False,
                review_required=False,
                expected_pass=True,
            ),
            V10IntegrationScenario(
                scenario_id="V10-INT-007",
                name="rejected orchestration fails closed",
                kind=V10IntegrationScenarioKind.REJECTED,
                execution_authorized=False,
                review_required=False,
                expected_pass=True,
            ),
            V10IntegrationScenario(
                scenario_id="V10-INT-008",
                name="architecture certification",
                kind=V10IntegrationScenarioKind.CERTIFICATION,
                execution_authorized=False,
                review_required=False,
                expected_pass=True,
            ),
        )


__all__ = [
    "CanonicalV10IntegrationScenarios",
    "V10IntegrationScenario",
    "V10IntegrationScenarioKind",
]
