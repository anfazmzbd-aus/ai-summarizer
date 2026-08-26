"""
V10 M10 compatibility and regression boundary.

Defines the formal compatibility domains and evaluates explicit
regression evidence for the V10 release.

This module does not execute tests, invoke runtime components, call
providers, or alter legacy V7/V8/V9 behavior.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class V10CompatibilityDomain(str, Enum):
    """Architecture domains that must remain compatible with V10."""

    V7_EXECUTION = "v7_execution"
    V8_RUNTIME = "v8_runtime"
    V9_PROVIDER = "v9_provider"
    V9_SUMMARIZATION = "v9_summarization"
    V9_RESILIENCE = "v9_resilience"
    V9_STREAMING = "v9_streaming"
    V10_INTELLIGENCE = "v10_intelligence"


class V10CompatibilityStatus(str, Enum):
    """Final compatibility disposition."""

    COMPATIBLE = "compatible"
    INCOMPATIBLE = "incompatible"


@dataclass(frozen=True, slots=True)
class V10CompatibilityRequirement:
    """One immutable architecture compatibility requirement."""

    domain: V10CompatibilityDomain
    description: str
    required: bool = True

    def __post_init__(self) -> None:
        if not isinstance(
            self.domain,
            V10CompatibilityDomain,
        ):
            raise TypeError("domain must be a V10CompatibilityDomain")

        if not isinstance(self.description, str):
            raise TypeError("description must be a string")

        if not self.description:
            raise ValueError("description must not be empty")

        if not isinstance(self.required, bool):
            raise TypeError("required must be a bool")


@dataclass(frozen=True, slots=True)
class V10CompatibilityManifest:
    """Immutable V10 compatibility boundary."""

    requirements: tuple[V10CompatibilityRequirement, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.requirements, tuple):
            raise TypeError("requirements must be a tuple")

        if not self.requirements:
            raise ValueError("requirements must not be empty")

        for requirement in self.requirements:
            if not isinstance(
                requirement,
                V10CompatibilityRequirement,
            ):
                raise TypeError(
                    "requirements must contain " "V10CompatibilityRequirement values"
                )

        domains = tuple(requirement.domain for requirement in self.requirements)

        if len(domains) != len(set(domains)):
            raise ValueError("compatibility domains must be unique")

    @property
    def required_domains(
        self,
    ) -> tuple[V10CompatibilityDomain, ...]:
        """Return domains that are mandatory for V10 release."""

        return tuple(
            requirement.domain
            for requirement in self.requirements
            if requirement.required
        )


@dataclass(frozen=True, slots=True)
class V10CompatibilityEvidence:
    """
    Explicit regression evidence supplied to compatibility evaluation.

    Test execution remains external to the intelligence architecture.
    """

    domain: V10CompatibilityDomain
    passed: bool
    reasons: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(
            self.domain,
            V10CompatibilityDomain,
        ):
            raise TypeError("domain must be a V10CompatibilityDomain")

        if not isinstance(self.passed, bool):
            raise TypeError("passed must be a bool")

        if not isinstance(self.reasons, tuple):
            raise TypeError("reasons must be a tuple")

        for reason in self.reasons:
            if not isinstance(reason, str):
                raise TypeError("reasons must contain strings")


@dataclass(frozen=True, slots=True)
class V10CompatibilityResult:
    """Immutable V10 compatibility certification result."""

    status: V10CompatibilityStatus

    manifest: V10CompatibilityManifest
    evidence: tuple[V10CompatibilityEvidence, ...]

    required_domains: int
    passed_domains: int
    failed_domains: int
    missing_domains: tuple[V10CompatibilityDomain, ...]

    reasons: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(
            self.status,
            V10CompatibilityStatus,
        ):
            raise TypeError("status must be a V10CompatibilityStatus")

        if not isinstance(
            self.manifest,
            V10CompatibilityManifest,
        ):
            raise TypeError("manifest must be a V10CompatibilityManifest")

        if not isinstance(self.evidence, tuple):
            raise TypeError("evidence must be a tuple")

        for item in self.evidence:
            if not isinstance(
                item,
                V10CompatibilityEvidence,
            ):
                raise TypeError(
                    "evidence must contain " "V10CompatibilityEvidence values"
                )

        for field_name, value in {
            "required_domains": self.required_domains,
            "passed_domains": self.passed_domains,
            "failed_domains": self.failed_domains,
        }.items():
            if not isinstance(value, int) or isinstance(value, bool):
                raise TypeError(f"{field_name} must be an integer")

            if value < 0:
                raise ValueError(f"{field_name} must be greater than " "or equal to 0")

        if not isinstance(
            self.missing_domains,
            tuple,
        ):
            raise TypeError("missing_domains must be a tuple")

        for domain in self.missing_domains:
            if not isinstance(
                domain,
                V10CompatibilityDomain,
            ):
                raise TypeError(
                    "missing_domains must contain " "V10CompatibilityDomain values"
                )

        if not isinstance(self.reasons, tuple):
            raise TypeError("reasons must be a tuple")

        for reason in self.reasons:
            if not isinstance(reason, str):
                raise TypeError("reasons must contain strings")

        if self.required_domains != len(self.manifest.required_domains):
            raise ValueError("required_domains must match manifest")

        if (
            self.passed_domains + self.failed_domains + len(self.missing_domains)
            != self.required_domains
        ):
            raise ValueError(
                "compatibility counts must account for " "all required domains"
            )

        has_failure = self.failed_domains > 0 or bool(self.missing_domains)

        if self.status is V10CompatibilityStatus.COMPATIBLE and has_failure:
            raise ValueError(
                "COMPATIBLE status cannot contain failed " "or missing required domains"
            )

        if self.status is V10CompatibilityStatus.INCOMPATIBLE and not has_failure:
            raise ValueError(
                "INCOMPATIBLE status requires a failed " "or missing required domain"
            )


class CanonicalV10CompatibilityManifest:
    """Factory for the V10 release compatibility boundary."""

    @staticmethod
    def build() -> V10CompatibilityManifest:
        return V10CompatibilityManifest(
            requirements=(
                V10CompatibilityRequirement(
                    domain=(V10CompatibilityDomain.V7_EXECUTION),
                    description=(
                        "V10 preserves established execution "
                        "graph, scheduling, and executor boundaries"
                    ),
                ),
                V10CompatibilityRequirement(
                    domain=(V10CompatibilityDomain.V8_RUNTIME),
                    description=(
                        "V10 preserves distributed runtime, "
                        "worker, retry, policy, and telemetry "
                        "responsibilities"
                    ),
                ),
                V10CompatibilityRequirement(
                    domain=(V10CompatibilityDomain.V9_PROVIDER),
                    description=(
                        "V10 does not replace or bypass "
                        "provider abstraction responsibilities"
                    ),
                ),
                V10CompatibilityRequirement(
                    domain=(V10CompatibilityDomain.V9_SUMMARIZATION),
                    description=(
                        "V10 preserves established chunking, "
                        "strategy, map-reduce, hierarchical, "
                        "and summarization pipeline behavior"
                    ),
                ),
                V10CompatibilityRequirement(
                    domain=(V10CompatibilityDomain.V9_RESILIENCE),
                    description=(
                        "V10 preserves quality-aware resilience "
                        "and fallback behavior"
                    ),
                ),
                V10CompatibilityRequirement(
                    domain=(V10CompatibilityDomain.V9_STREAMING),
                    description=(
                        "V10 preserves established streaming " "summarization behavior"
                    ),
                ),
                V10CompatibilityRequirement(
                    domain=(V10CompatibilityDomain.V10_INTELLIGENCE),
                    description=(
                        "V10 intelligence regression remains "
                        "fully compatible with the release "
                        "architecture"
                    ),
                ),
            )
        )


class V10CompatibilityEvaluator:
    """Evaluate explicit regression evidence against release requirements."""

    def evaluate(
        self,
        manifest: V10CompatibilityManifest,
        evidence: tuple[V10CompatibilityEvidence, ...],
    ) -> V10CompatibilityResult:
        if not isinstance(
            manifest,
            V10CompatibilityManifest,
        ):
            raise TypeError("manifest must be a V10CompatibilityManifest")

        if not isinstance(evidence, tuple):
            raise TypeError("evidence must be a tuple")

        for item in evidence:
            if not isinstance(
                item,
                V10CompatibilityEvidence,
            ):
                raise TypeError(
                    "evidence must contain " "V10CompatibilityEvidence values"
                )

        evidence_domains = tuple(item.domain for item in evidence)

        if len(evidence_domains) != len(set(evidence_domains)):
            raise ValueError("compatibility evidence domains must be unique")

        evidence_by_domain = {item.domain: item for item in evidence}

        required = manifest.required_domains

        missing_domains = tuple(
            domain for domain in required if domain not in evidence_by_domain
        )

        supplied_required = tuple(
            evidence_by_domain[domain]
            for domain in required
            if domain in evidence_by_domain
        )

        passed_domains = sum(item.passed for item in supplied_required)

        failed_domains = sum(not item.passed for item in supplied_required)

        has_failure = failed_domains > 0 or bool(missing_domains)

        status = (
            V10CompatibilityStatus.INCOMPATIBLE
            if has_failure
            else V10CompatibilityStatus.COMPATIBLE
        )

        reasons = self._build_reasons(
            supplied_required=supplied_required,
            missing_domains=missing_domains,
        )

        return V10CompatibilityResult(
            status=status,
            manifest=manifest,
            evidence=evidence,
            required_domains=len(required),
            passed_domains=passed_domains,
            failed_domains=failed_domains,
            missing_domains=missing_domains,
            reasons=reasons,
        )

    @staticmethod
    def _build_reasons(
        *,
        supplied_required: tuple[V10CompatibilityEvidence, ...],
        missing_domains: tuple[V10CompatibilityDomain, ...],
    ) -> tuple[str, ...]:
        reasons: list[str] = []

        for item in supplied_required:
            if item.passed:
                reasons.append(f"{item.domain.value} compatibility passed")
            else:
                reasons.append(f"{item.domain.value} compatibility failed")

        for domain in missing_domains:
            reasons.append(f"{domain.value} compatibility evidence missing")

        if all(item.passed for item in supplied_required) and not missing_domains:
            reasons.append("V10 compatibility and regression boundary passed")
        else:
            reasons.append("V10 compatibility and regression boundary failed")

        return tuple(reasons)


__all__ = [
    "CanonicalV10CompatibilityManifest",
    "V10CompatibilityDomain",
    "V10CompatibilityEvidence",
    "V10CompatibilityEvaluator",
    "V10CompatibilityManifest",
    "V10CompatibilityRequirement",
    "V10CompatibilityResult",
    "V10CompatibilityStatus",
]
