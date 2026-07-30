from app.runtime.intelligence.execution_strategy import (
    ExecutionStrategy,
)
from app.runtime.intelligence.strategy_types import (
    ExecutionStrategyType,
)
from app.runtime.observability.strategy_snapshot import (
    StrategySnapshot,
)


def test_strategy_snapshot():
    strategy = ExecutionStrategy(
        strategy=ExecutionStrategyType.DEFAULT,
        parallel_execution=True,
        use_cache=False,
        enable_retry=False,
        checkpoint_enabled=False,
        timeout_multiplier=1.0,
    )

    snapshot = StrategySnapshot(
        strategy=strategy,
    )

    assert snapshot.strategy is strategy
