"""
AI Summarizer V8.0 Distributed Runtime

Execution queue abstraction.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.distributed.protocols import TaskEnvelope


class ExecutionQueue(ABC):
    """
    Abstract distributed execution queue.

    Implementations:
    - Local async queue
    - Redis queue
    - RabbitMQ queue
    - Kafka queue
    """

    @abstractmethod
    async def enqueue(
        self,
        task: TaskEnvelope,
    ) -> None:
        """
        Add task to queue.
        """

    @abstractmethod
    async def dequeue(
        self,
    ) -> TaskEnvelope:
        """
        Retrieve next task.
        """

    @abstractmethod
    def size(self) -> int:
        """
        Return queue size.
        """

    @abstractmethod
    def empty(self) -> bool:
        """
        Check whether queue is empty.
        """

    @abstractmethod
    async def clear(self) -> None:
        """
        Remove all queued tasks.
        """
