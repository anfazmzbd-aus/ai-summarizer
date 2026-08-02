"""
AI Summarizer V8.0

Production Retry Manager.
"""

from __future__ import annotations

import asyncio

from app.distributed.protocols import TaskEnvelope
from app.distributed.queue import ExecutionQueue

from .dead_letter_queue import DeadLetterQueue
from .retry_policy import RetryPolicy


class RetryManager:
    """
    Coordinates retry scheduling.

    Responsibilities
    ----------------
    - Retry scheduling
    - Backoff
    - Dead-letter routing
    """

    def __init__(
        self,
        queue: ExecutionQueue,
        policy: RetryPolicy,
        dead_letter_queue: DeadLetterQueue,
    ) -> None:

        self._queue = queue
        self._policy = policy
        self._dead_letter_queue = dead_letter_queue

    async def handle_failure(
        self,
        task: TaskEnvelope,
    ) -> bool:
        """
        Returns True if task was requeued.
        """

        if not self._policy.should_retry(
            task.retry_count,
        ):

            self._dead_letter_queue.add(task)

            return False

        delay = self._policy.next_delay(
            task.retry_count,
        )

        if delay > 0:
            await asyncio.sleep(delay)

        task.increment_retry()

        await self._queue.enqueue(task)

        return True

    def dead_letter_count(
        self,
    ) -> int:

        return self._dead_letter_queue.size()
