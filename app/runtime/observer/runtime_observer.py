from __future__ import annotations

from .observer_context import ObserverContext


class RuntimeObserver:
    """
    Collects runtime observations.

    This class is passive and has no effect on execution.
    """

    def __init__(
        self,
        context: ObserverContext,
    ) -> None:
        self._context = context

    @property
    def context(self) -> ObserverContext:
        return self._context

    def execution_started(self) -> None:
        self._context.record("execution_started")

    def execution_finished(self) -> None:
        self._context.record("execution_finished")

    def layer_started(
        self,
        index: int,
    ) -> None:
        self._context.current_layer = index
        self._context.record(f"layer_started:{index}")

    def layer_finished(
        self,
        index: int,
    ) -> None:
        self._context.record(f"layer_finished:{index}")

    def node_started(
        self,
        node: str,
    ) -> None:
        self._context.current_node = node
        self._context.record(f"node_started:{node}")

    def node_finished(
        self,
        node: str,
    ) -> None:
        self._context.record(f"node_finished:{node}")
