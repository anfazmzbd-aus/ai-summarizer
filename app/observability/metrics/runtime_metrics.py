"""
Runtime metrics.
"""

from __future__ import annotations

from .counter import Counter
from .gauge import Gauge
from .histogram import Histogram
from .metrics_registry import MetricsRegistry


class RuntimeMetrics:

    def __init__(
        self,
        registry: MetricsRegistry,
    ) -> None:

        self.registry = registry

        self.tasks_submitted = registry.register(Counter("runtime.tasks.submitted"))

        self.tasks_completed = registry.register(Counter("runtime.tasks.completed"))

        self.tasks_failed = registry.register(Counter("runtime.tasks.failed"))

        self.retries = registry.register(Counter("runtime.tasks.retries"))

        self.dead_letters = registry.register(Counter("runtime.tasks.dead_letters"))

        self.queue_depth = registry.register(Gauge("runtime.queue.depth"))

        self.active_workers = registry.register(Gauge("runtime.workers.active"))

        self.execution_latency = registry.register(
            Histogram("runtime.execution.latency_ms")
        )

    def task_submitted(self) -> None:

        self.tasks_submitted.increment()

    def task_completed(
        self,
        latency_ms: float,
    ) -> None:

        self.tasks_completed.increment()

        self.execution_latency.observe(latency_ms)

    def task_failed(self) -> None:

        self.tasks_failed.increment()

    def retry(self) -> None:

        self.retries.increment()

    def dead_letter(self) -> None:

        self.dead_letters.increment()

    def set_queue_depth(
        self,
        depth: int,
    ) -> None:

        self.queue_depth.set(depth)

    def set_active_workers(
        self,
        count: int,
    ) -> None:

        self.active_workers.set(count)
