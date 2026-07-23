from app.orchestration.registry.agent_registry import AgentRegistry
from app.runtime.retry_executor import RetryExecutor
from app.runtime.retry_policy import RetryPolicy
from app.runtime.runtime_config import RuntimeConfig

from .node_execution_result import NodeExecutionResult


class NodeExecutor:

    def __init__(
        self,
        registry: AgentRegistry,
        contracts,
        events=None,
    ):

        self.registry = registry
        self.contracts = contracts
        self.events = events

        config = RuntimeConfig()

        self._retry_executor = RetryExecutor(
            RetryPolicy(
                enabled=config.retry_enabled,
                max_attempts=config.max_retry_attempts,
                delay_seconds=config.retry_delay_seconds,
                exponential_backoff=config.retry_exponential_backoff,
            )
        )

    def execute(
        self,
        node,
        state,
    ):

        if self.events:

            if hasattr(
                self.events,
                "node_started",
            ):
                self.events.node_started(node)

            else:
                from app.runtime.events.event_types import NodeStarted

                self.events.publish(
                    NodeStarted(
                        execution_id="runtime",
                        node=node,
                    )
                )

        spec = self.registry.get(node)

        result = self._retry_executor.run(
            spec.agent.run,
            state,
        )

        self.contracts.validate_output(
            node,
            result,
        )

        try:
            if self.events:
                if hasattr(
                    self.events,
                    "node_finished",
                ):
                    self.events.node_finished(node)

                else:
                    from app.runtime.events.event_types import NodeFinished

                    self.events.publish(
                        NodeFinished(
                            execution_id="runtime",
                            node=node,
                        )
                    )

            return NodeExecutionResult(
                node=node,
                output=result,
            )

        except Exception:

            if self.events:
                self.events.node_failed(node)

            raise
