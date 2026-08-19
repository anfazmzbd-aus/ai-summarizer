"""
V10 strategy handoff policy.

Defines advisory and mandatory strategy policies at the V10/V9.3 boundary.

The policy does not select a strategy. The existing V9.3 planner remains
authoritative for strategy selection.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from app.summarization.strategies.models import SummarizationStrategyType


@dataclass(frozen=True, slots=True)
class StrategyHandoffPolicy:
    """
    Immutable policy governing how a V10 decision relates to V9.3 strategy
    selection.

    preferred_strategy is advisory.

    allowed_strategies and required_strategy are enforcement constraints.
    """

    preferred_strategy: SummarizationStrategyType | None = None
    allowed_strategies: tuple[SummarizationStrategyType, ...] = ()
    required_strategy: SummarizationStrategyType | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.preferred_strategy is not None and not isinstance(
            self.preferred_strategy,
            SummarizationStrategyType,
        ):
            raise TypeError(
                "preferred_strategy must be a SummarizationStrategyType or None"
            )

        if not isinstance(self.allowed_strategies, tuple):
            raise TypeError("allowed_strategies must be a tuple")

        for strategy in self.allowed_strategies:
            if not isinstance(strategy, SummarizationStrategyType):
                raise TypeError(
                    "allowed_strategies must contain only "
                    "SummarizationStrategyType values"
                )

        if self.required_strategy is not None and not isinstance(
            self.required_strategy,
            SummarizationStrategyType,
        ):
            raise TypeError(
                "required_strategy must be a SummarizationStrategyType or None"
            )

        if (
            self.required_strategy is not None
            and self.allowed_strategies
            and self.required_strategy not in self.allowed_strategies
        ):
            raise ValueError("required_strategy must be included in allowed_strategies")

        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")

        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(dict(self.metadata)),
        )

    @property
    def is_advisory_only(self) -> bool:
        """Return whether the policy contains only a preference."""
        return (
            self.preferred_strategy is not None
            and not self.allowed_strategies
            and self.required_strategy is None
        )

    @property
    def has_hard_constraint(self) -> bool:
        """Return whether the policy contains an enforcement constraint."""
        return bool(self.allowed_strategies or self.required_strategy is not None)

    @classmethod
    def from_mapping(
        cls,
        values: Mapping[str, Any],
    ) -> "StrategyHandoffPolicy":
        """
        Build a strategy policy from V10 context constraints.

        Supported keys:
            preferred_strategy
            allowed_strategies
            required_strategy
        """
        if not isinstance(values, Mapping):
            raise TypeError("strategy policy values must be a mapping")

        preferred_raw = values.get("preferred_strategy")
        preferred = cls._parse_strategy(
            preferred_raw,
            field_name="preferred_strategy",
        )

        allowed_raw = values.get("allowed_strategies", ())
        if allowed_raw is None:
            allowed_raw = ()

        if isinstance(allowed_raw, str):
            allowed_raw = (allowed_raw,)

        if not isinstance(allowed_raw, (tuple, list, set, frozenset)):
            raise TypeError("allowed_strategies must be a sequence of strategy names")

        allowed = tuple(
            cls._parse_strategy(
                value,
                field_name="allowed_strategies",
            )
            for value in allowed_raw
        )

        required = cls._parse_strategy(
            values.get("required_strategy"),
            field_name="required_strategy",
        )

        return cls(
            preferred_strategy=preferred,
            allowed_strategies=allowed,
            required_strategy=required,
        )

    @staticmethod
    def _parse_strategy(
        value: Any,
        *,
        field_name: str,
    ) -> SummarizationStrategyType | None:
        if value is None:
            return None

        if isinstance(value, SummarizationStrategyType):
            return value

        if not isinstance(value, str):
            if field_name == "preferred_strategy":
                raise TypeError("preferred_strategy must be a strategy name or None")

            if field_name == "required_strategy":
                raise TypeError("required_strategy must be a strategy name or None")

            raise TypeError("allowed_strategies values must be strategy names")

        try:
            return SummarizationStrategyType(value)
        except ValueError as exc:
            raise ValueError(f"unsupported summarization strategy: {value}") from exc


__all__ = ["StrategyHandoffPolicy"]
