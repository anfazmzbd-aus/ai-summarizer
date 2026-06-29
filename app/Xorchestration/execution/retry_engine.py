from copy import deepcopy
from dataclasses import dataclass
from typing import Optional
from typing import Callable
from time import monotonic
from time import sleep

from app.orchestration.graph.graph_schema import (
    GraphNode,
)

from app.orchestration.state.state_model import (
    State,
)

from app.orchestration.execution.execution_context import (
    ExecutionContext,
)


# ------------------------
# Retry Snapshot
# ------------------------

@dataclass(frozen=True)
class RetrySnapshot:

    node_name: str

    state_snapshot: State

    captured_at_ms: float


# ------------------------
# Retry Result
# ------------------------

@dataclass(frozen=True)
class RetryResult:

    success: bool

    attempts: int

    final_error: Optional[
        Exception
    ] = None


# ------------------------
# Retry Policy
# ------------------------

@dataclass(frozen=True)
class RetryPolicy:

    max_attempts: int

    base_delay_ms: int = 250

    exponential: bool = True


# ------------------------
# Engine
# ------------------------

class RetryEngine:

    def __init__(self):

        self.snapshots = {}

    def should_retry(
        self,
        node: GraphNode,
        attempt: int,
        error: Exception,
    ) -> bool:

        if not node.retryable:

            return False

        return (
            attempt
            <=
            node.max_retries
        )

    # -------------------

    def capture_snapshot(
        self,
        node: GraphNode,
        state: State,
    ) -> RetrySnapshot:

        snapshot = RetrySnapshot(

            node_name=node.name,

            state_snapshot=(
                deepcopy(
                    state
                )
            ),

            captured_at_ms=(
                monotonic()
            ),
        )

        self.snapshots[
            node.name
        ] = snapshot

        return snapshot

    # -------------------

    def execute_with_retry(
        self,
        node: GraphNode,
        state: State,
        context: ExecutionContext,
        execute_fn: Callable,
    ):

        snapshot = (
            self.capture_snapshot(
                node,
                state,
            )
        )

        attempts = 0

        last_error = None

        while True:

            try:

                attempts += 1

                return (
                    execute_fn(
                        snapshot
                        .state_snapshot
                    )
                )

            except Exception as e:

                last_error = e

                context.runtime[
                    node.name
                ].retries += 1

                if not self.should_retry(
                    node=node,
                    attempt=attempts,
                    error=e,
                ):

                    raise

                self._apply_backoff(
                    attempts
                )

    # -------------------

    def on_retry(
        self,
        node: GraphNode,
        attempt: int,
        error: Exception,
    ):

        return None

    # -------------------

    def _apply_backoff(
        self,
        attempt: int,
    ):

        delay = (
            0.25
            *
            (
                2
                **
                (
                    attempt
                    -
                    1
                )
            )
        )

        sleep(
            delay
        )

    # -------------------

    def clear(
        self,
        node_name: str,
    ):

        self.snapshots.pop(
            node_name,
            None
        )