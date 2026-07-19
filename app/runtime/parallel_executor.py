"""
AI Summarizer V7.8 Parallel Executor
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from concurrent.futures import ThreadPoolExecutor
from typing import Any


class ParallelExecutor:
    """
    Executes independent callables in parallel while preserving
    deterministic result ordering.
    """

    def __init__(self, max_workers: int = 4) -> None:
        self.max_workers = max_workers

    def execute(
        self,
        func: Callable[..., Any],
        items: Iterable[Any],
    ) -> list[Any]:
        """
        Executes func(item) for every item.

        Results preserve input ordering.
        """

        items = list(items)

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            return list(executor.map(func, items))
