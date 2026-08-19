"""
V10 planning constraint contract.

Defines the constraints that V10 may enforce at the boundary around the
existing V9.3 summarization planner.

The contract is provider-independent and does not modify V9.3 planning.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping

from app.summarization.strategies.models import SummarizationStrategyType


@dataclass(frozen=True, slots=True)
class PlanningConstraints:
    """
    Immutable constraints applicable to V9.3 planning.

    Only constraints that can be enforced without changing the V9.3 planner
    are represented here.
    """

    max_input_tokens: int | None = None
    max_chunks: int | None = None
    allowed_strategies: tuple[SummarizationStrategyType, ...] = ()
    required_strategy: SummarizationStrategyType | None = None
    metadata: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.max_input_tokens is not None:
            if not isinstance(self.max_input_tokens, int):
                raise TypeError("max_input_tokens must be an integer or None")
            if self.max_input_tokens <= 0:
                raise ValueError("max_input_tokens must be greater than zero")

        if self.max_chunks is not None:
            if not isinstance(self.max_chunks, int):
                raise TypeError("max_chunks must be an integer or None")
            if self.max_chunks <= 0:
                raise ValueError("max_chunks must be greater than zero")

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
    def has_strategy_constraint(self) -> bool:
        """Return whether strategy selection is constrained."""
        return bool(self.allowed_strategies or self.required_strategy)

    @classmethod
    def from_mapping(
        cls,
        constraints: Mapping[str, object],
    ) -> "PlanningConstraints":
        """
        Build typed planning constraints from IntelligenceContext constraints.
        """
        if not isinstance(constraints, Mapping):
            raise TypeError("constraints must be a mapping")

        allowed_raw = constraints.get("allowed_strategies", ())
        if allowed_raw is None:
            allowed_raw = ()

        if isinstance(allowed_raw, str):
            allowed_raw = (allowed_raw,)

        if not isinstance(allowed_raw, (tuple, list, set, frozenset)):
            raise TypeError("allowed_strategies must be a sequence of strategy names")

        allowed: list[SummarizationStrategyType] = []

        for value in allowed_raw:
            if isinstance(value, SummarizationStrategyType):
                allowed.append(value)
                continue

            if not isinstance(value, str):
                raise TypeError("allowed_strategies values must be strategy names")

            try:
                allowed.append(SummarizationStrategyType(value))
            except ValueError as exc:
                raise ValueError(
                    f"unsupported summarization strategy: {value}"
                ) from exc

        required_raw = constraints.get("required_strategy")

        required: SummarizationStrategyType | None = None

        if required_raw is not None:
            if isinstance(required_raw, SummarizationStrategyType):
                required = required_raw
            elif isinstance(required_raw, str):
                try:
                    required = SummarizationStrategyType(required_raw)
                except ValueError as exc:
                    raise ValueError(
                        f"unsupported summarization strategy: {required_raw}"
                    ) from exc
            else:
                raise TypeError("required_strategy must be a strategy name or None")

        return cls(
            max_input_tokens=constraints.get("max_input_tokens"),  # type: ignore[arg-type]
            max_chunks=constraints.get("max_chunks"),  # type: ignore[arg-type]
            allowed_strategies=tuple(allowed),
            required_strategy=required,
        )


__all__ = ["PlanningConstraints"]
