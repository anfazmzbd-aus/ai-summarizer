from app.runtime.cancellation_token import CancellationToken
from app.runtime.runtime_config import RuntimeConfig
from app.runtime.runtime_context import RuntimeContext
from app.runtime.runtime_metadata import RuntimeMetadata, RuntimeStatus


def test_initial_state():
    context = RuntimeContext(
        execution_context=None,
        config=RuntimeConfig(),
        metadata=RuntimeMetadata(),
        cancellation_token=CancellationToken(),
    )

    assert context.metadata.status == RuntimeStatus.NEW


def test_mark_completed():
    context = RuntimeContext(
        execution_context=None,
        config=RuntimeConfig(),
        metadata=RuntimeMetadata(),
        cancellation_token=CancellationToken(),
    )

    context.mark_completed()

    assert context.metadata.status == RuntimeStatus.COMPLETED
    assert context.metadata.completed_at is not None
