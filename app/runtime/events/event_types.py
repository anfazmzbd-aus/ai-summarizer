from dataclasses import dataclass


@dataclass(frozen=True)
class ExecutionStarted:
    execution_id: str


@dataclass(frozen=True)
class ExecutionFinished:
    execution_id: str


@dataclass(frozen=True)
class LayerStarted:
    execution_id: str
    layer_index: int


@dataclass(frozen=True)
class LayerFinished:
    execution_id: str
    layer_index: int


@dataclass(frozen=True)
class NodeStarted:
    execution_id: str
    node: str


@dataclass(frozen=True)
class NodeFinished:
    execution_id: str
    node: str


@dataclass(frozen=True)
class NodeFailed:
    execution_id: str
    node: str
    error: str


@dataclass(frozen=True)
class RetryStarted:
    execution_id: str
    node: str
    attempt: int


@dataclass(frozen=True)
class RetryFinished:
    execution_id: str
    node: str
    attempt: int
