# app/orchestration/graph/graph_exceptions.py

class GraphError(Exception):
    pass


class DuplicateNodeError(GraphError):
    pass


class MissingDependencyError(GraphError):
    pass


class CycleDetectedError(GraphError):
    pass


class LayerConstructionError(GraphError):
    pass