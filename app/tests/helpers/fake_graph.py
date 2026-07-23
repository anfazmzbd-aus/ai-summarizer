from unittest.mock import Mock

from app.tests.helpers.builders import make_layer


def make_graph(*layers):

    graph = Mock()

    graph.layers = [
        make_layer(*layer, index=index) for index, layer in enumerate(layers)
    ]

    return graph
