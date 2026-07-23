from unittest.mock import Mock

from app.orchestration.execution.node_executor import NodeExecutor


def test_node_executor_emits_events():

    registry = Mock()
    contracts = Mock()

    agent = Mock()
    agent.run.return_value = {}

    registry.get.return_value.agent = agent

    publisher = Mock()

    executor = NodeExecutor(
        registry,
        contracts,
        publisher,
    )

    executor.execute(
        "summary",
        Mock(),
    )

    publisher.node_started.assert_called_once_with("summary")

    publisher.node_finished.assert_called_once_with("summary")
