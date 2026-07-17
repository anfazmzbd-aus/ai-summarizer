from dataclasses import FrozenInstanceError

import pytest

from app.runtime.runtime_config import RuntimeConfig


def test_default_configuration() -> None:
    config = RuntimeConfig()

    assert config.parallel_enabled is False
    assert config.max_workers == 1
    assert config.retry_enabled is False
    assert config.retry_attempts == 0
    assert config.metrics_enabled is True


def test_configuration_is_immutable() -> None:
    config = RuntimeConfig()

    with pytest.raises(FrozenInstanceError):
        config.max_workers = 8
