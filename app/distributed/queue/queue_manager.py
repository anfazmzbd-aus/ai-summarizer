"""
AI Summarizer V8.0 Distributed Runtime

Queue factory and manager.
"""

from __future__ import annotations

from .local_queue import LocalExecutionQueue
from .queue_interface import ExecutionQueue


class QueueManager:
    """
    Creates execution queue implementations.

    Future backends:
    - Redis
    - RabbitMQ
    - Kafka
    """

    @staticmethod
    def create(
        backend: str = "local",
        **kwargs,
    ) -> ExecutionQueue:

        if backend == "local":

            return LocalExecutionQueue(**kwargs)

        raise ValueError(f"Unsupported queue backend: {backend}")
