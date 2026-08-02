"""
Remote executor interface.
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from app.distributed.protocols import TaskEnvelope

from .execution_result import RemoteExecutionResult


class RemoteExecutor(ABC):

    @abstractmethod
    async def execute(
        self,
        task: TaskEnvelope,
    ) -> RemoteExecutionResult:
        """
        Execute a task on a target runtime.
        """
