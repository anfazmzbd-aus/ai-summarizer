from unittest.mock import Mock


def make_state():
    state = Mock()

    state.global_context = {}
    state.artifacts = {}
    state.node_outputs = {}

    return state
