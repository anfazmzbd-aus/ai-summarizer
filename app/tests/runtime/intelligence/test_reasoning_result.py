import pytest
from dataclasses import FrozenInstanceError
from app.runtime.intelligence.reasoning_result import ReasoningResult


def test_tc_rr_001_reasoning_result_creation():
    result = ReasoningResult(
        workload_size=10,
        estimated_parallelism=3,
        cache_available=True,
        cancellation_requested=False,
        timeout_risk=False,
        retry_pressure=False,
        policy_restricted=False,
    )
    assert result.workload_size == 10


def test_tc_rr_002_immutable_result():
    result = ReasoningResult(
        workload_size=1,
        estimated_parallelism=3,
        cache_available=True,
        cancellation_requested=False,
        timeout_risk=False,
        retry_pressure=False,
        policy_restricted=False,
    )
    with pytest.raises(FrozenInstanceError):
        result.workload_size = 5


def test_tc_rr_003_equality_validation():
    result1 = ReasoningResult(
        workload_size=5,
        estimated_parallelism=2,
        cache_available=True,
        cancellation_requested=False,
        timeout_risk=False,
        retry_pressure=False,
        policy_restricted=False,
    )
    result2 = ReasoningResult(
        workload_size=5,
        estimated_parallelism=2,
        cache_available=True,
        cancellation_requested=False,
        timeout_risk=False,
        retry_pressure=False,
        policy_restricted=False,
    )
    assert result1 == result2


def test_tc_rr_004_different_runtime_observations_differ():
    result1 = ReasoningResult(
        workload_size=5,
        estimated_parallelism=2,
        cache_available=True,
        cancellation_requested=False,
        timeout_risk=False,
        retry_pressure=False,
        policy_restricted=False,
    )
    result2 = ReasoningResult(
        workload_size=10,
        estimated_parallelism=3,
        cache_available=True,
        cancellation_requested=False,
        timeout_risk=False,
        retry_pressure=False,
        policy_restricted=False,
    )
    assert result1 != result2
