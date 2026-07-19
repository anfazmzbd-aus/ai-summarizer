# from app.orchestration import state
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
    ):

        self.registry = registry
        self.contracts = contracts

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

        spec = self.registry.get(node)

        result = self._retry_executor.run(
            spec.agent.run,
            state,
        )

        self.contracts.validate_output(
            node,
            result,
        )

        return NodeExecutionResult(
            node=node,
            output=result,
        )
