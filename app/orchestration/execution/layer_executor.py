from functools import partial

from app.runtime.parallel_executor import ParallelExecutor
from app.runtime.runtime_config import RuntimeConfig


class LayerExecutor:

    def __init__(
        self,
        node_executor,
        runtime_config: RuntimeConfig | None = None,
        parallel_executor: ParallelExecutor | None = None,
        events=None,
    ):

        self.node_executor = node_executor

        self.events = events

        self._config = runtime_config or RuntimeConfig()

        self._parallel_executor = parallel_executor or ParallelExecutor(
            max_workers=self._config.max_workers,
        )

    def execute_layer(
        self,
        layer,
        state,
        runtime_config: RuntimeConfig | None = None,
    ):

        nodes = list(layer.nodes)

        if self.events:
            self.events.layer_started(
                layer.index,
            )

        config = runtime_config or self._config

        if config.parallel_execution and len(nodes) > 1:

            execute = partial(
                self.node_executor.execute,
                state=state,
            )

            executions = self._parallel_executor.execute(
                execute,
                nodes,
            )

        else:

            executions = [
                self.node_executor.execute(
                    node,
                    state,
                )
                for node in nodes
            ]

        for execution in executions:

            state.node_outputs[execution.node] = execution.output

            state.artifacts.update(execution.output)

        if self.events:
            self.events.layer_finished(
                layer.index,
            )
