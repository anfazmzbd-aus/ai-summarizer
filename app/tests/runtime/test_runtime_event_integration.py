from unittest.mock import Mock

from app.orchestration.execution.node_executor import NodeExecutor


def test_node_executor_uses_event_publisher():

    registry = Mock()
    contracts = Mock()
    events = Mock()

    agent = Mock()
    agent.run.return_value = {}

    registry.get.return_value.agent = agent

    executor = NodeExecutor(
        registry,
        contracts,
        events,
    )

    executor.execute(
        "summary",
        Mock(),
    )

    events.node_started.assert_called_once_with("summary")

    events.node_finished.assert_called_once_with("summary")
