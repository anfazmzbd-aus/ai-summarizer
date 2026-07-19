from dataclasses import FrozenInstanceError

import pytest

from app.runtime.runtime_config import RuntimeConfig


def test_default_configuration() -> None:
    config = RuntimeConfig()

    assert config.parallel_enabled is False
    # assert config.max_workers == 1
    assert config.metrics_enabled is True
    assert config.retry_enabled is True
    assert config.max_retry_attempts == 3
    assert config.retry_delay_seconds == 0.0
    assert config.retry_exponential_backoff is False
    assert config.parallel_execution is False
    assert config.max_workers == 4


def test_configuration_is_immutable() -> None:
    config = RuntimeConfig()

    with pytest.raises(FrozenInstanceError):
        config.max_workers = 8
