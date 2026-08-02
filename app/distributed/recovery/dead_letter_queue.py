"""
Dead letter queue.
"""

from __future__ import annotations

from app.distributed.protocols import TaskEnvelope


class DeadLetterQueue:

    def __init__(self) -> None:

        self._tasks: list[TaskEnvelope] = []

    def add(
        self,
        task: TaskEnvelope,
    ) -> None:

        self._tasks.append(task)

    def size(self) -> int:

        return len(self._tasks)

    def all(self) -> list[TaskEnvelope]:

        return list(self._tasks)
