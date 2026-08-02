"""
Failure handler.
"""

from __future__ import annotations

from app.distributed.protocols import TaskEnvelope

from .dead_letter_queue import DeadLetterQueue
from .retry_policy import RetryPolicy


class FailureHandler:

    def __init__(
        self,
        policy: RetryPolicy,
        dead_letter_queue: DeadLetterQueue,
    ) -> None:

        self.policy = policy

        self.dead_letter_queue = dead_letter_queue

    def process_failure(
        self,
        task: TaskEnvelope,
    ) -> bool:
        """
        Returns True if task should be retried.
        """

        task.increment_retry()

        if self.policy.should_retry(task.retry_count):

            return True

        self.dead_letter_queue.add(task)

        return False
