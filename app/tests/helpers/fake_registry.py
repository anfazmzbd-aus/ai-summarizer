from unittest.mock import Mock


def make_registry(agent):

    registry = Mock()

    spec = Mock()
    spec.agent = agent

    registry.get.return_value = spec

    return registry
