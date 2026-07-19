from unittest.mock import Mock

import pytest

from app.orchestration.execution.node_executor import NodeExecutor


class FakeAgent:
    def __init__(self):
        self.calls = 0

    def run(self, state):
        self.calls += 1
        return {"summary": "ok"}


class RetryAgent:
    def __init__(self):
        self.calls = 0

    def run(self, state):
        self.calls += 1

        if self.calls == 1:
            raise RuntimeError("temporary")

        return {"summary": "ok"}


class FailingAgent:
    def __init__(self):
        self.calls = 0

    def run(self, state):
        self.calls += 1
        raise RuntimeError("failure")


def make_executor(agent):
    registry = Mock()
    contracts = Mock()

    spec = Mock()
    spec.agent = agent

    registry.get.return_value = spec

    return (
        NodeExecutor(
            registry=registry,
            contracts=contracts,
        ),
        contracts,
    )


def make_state():
    state = Mock()
    state.node_outputs = {}
    state.artifacts = {}
    return state


def test_node_executor_success_first_attempt():
    executor, contracts = make_executor(FakeAgent())
    state = make_state()

    result = executor.execute(
        "summary",
        state,
    )

    assert result.output["summary"] == "ok"
    contracts.validate_output.assert_called_once()


def test_node_executor_retry_then_success():
    agent = RetryAgent()

    executor, contracts = make_executor(agent)
    state = make_state()

    result = executor.execute(
        "summary",
        state,
    )

    assert result.output["summary"] == "ok"
    assert agent.calls == 2
    contracts.validate_output.assert_called_once()


def test_node_executor_retry_failure():
    agent = FailingAgent()

    executor, _ = make_executor(agent)
    state = make_state()

    with pytest.raises(RuntimeError):
        executor.execute(
            "summary",
            state,
        )

    assert agent.calls == 3
