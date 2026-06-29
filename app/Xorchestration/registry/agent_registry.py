from dataclasses import dataclass
from dataclasses import field

from typing import Any
from typing import Callable

from app.orchestration.state.state_contracts import (
    StateContract,
)


# ------------------------
# Retry Policy
# ------------------------

@dataclass(
    frozen=True
)
class RetryPolicy:

    retryable: bool = True

    max_retries: int = 1

    timeout_seconds: float = 30


# ------------------------
# Agent Specification
# ------------------------

@dataclass(
    frozen=True
)
class AgentSpec:

    name: str

    function_name: str

    agent: Any

    contract: StateContract

    dependencies: tuple[
        str,
        ...
    ] = ()

    reads: frozenset[
        str
    ] = frozenset()

    writes: frozenset[
        str
    ] = frozenset()

    retry: RetryPolicy = (
        RetryPolicy()
    )

    metadata: dict[
        str,
        Any
    ] = field(
        default_factory=dict
    )


# ------------------------
# Registry
# ------------------------

class AgentRegistry:

    def __init__(self):

        self._agents = {}

    # --------------------

    def register(
        self,
        spec: AgentSpec,
    ):

        if (
            spec.name
            in
            self._agents
        ):

            raise ValueError(
                f"{spec.name} already registered"
            )

        self._agents[
            spec.name
        ] = spec

    # --------------------

    def get(
        self,
        name: str,
    ) -> AgentSpec:

        if (
            name
            not in
            self._agents
        ):

            raise KeyError(
                f"{name} not registered"
            )

        return (
            self._agents[
                name
            ]
        )

    # --------------------

    def resolve(
        self,
        name,
    ):

        return (
            self
            .get(
                name
            )
            .agent
        )

    # --------------------

    def exists(
        self,
        name,
    ):

        return (
            name
            in
            self._agents
        )

    # --------------------

    def list_agents(
        self,
    ):

        return tuple(

            sorted(
                self._agents
            )

        )

    # --------------------

    def contracts(
        self,
    ):

        return {

            k: v.contract

            for k, v

            in

            self._agents.items()

        }