from app.orchestration.execution.execution_context import ExecutionContext

from app.runtime.cancellation_token import CancellationToken
from app.runtime.runtime_config import RuntimeConfig
from app.runtime.runtime_context import RuntimeContext
from app.runtime.runtime_metadata import RuntimeMetadata


def test_runtime_context_creation() -> None:
    context = RuntimeContext(
        execution_context=ExecutionContext(),
        config=RuntimeConfig(),
        metadata=RuntimeMetadata(),
        cancellation_token=CancellationToken(),
    )

    assert context.config.metrics_enabled
    assert context.metadata.execution_id is not None
    assert context.cancellation_token.cancelled is False
