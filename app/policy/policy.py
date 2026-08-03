"""
Base policy contract.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.distributed.protocols import TaskEnvelope

from .result import PolicyResult


class Policy(ABC):

    @abstractmethod
    def evaluate(
        self,
        task: TaskEnvelope,
    ) -> PolicyResult: ...
