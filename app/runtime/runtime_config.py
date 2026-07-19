"""
AI Summarizer V7.8 Runtime Configuration

Defines immutable runtime configuration used during a single execution.
This configuration is created by the RuntimeManager and remains immutable
for the lifetime of the execution.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RuntimeConfig:
    """
    Immutable runtime configuration.

    The configuration controls runtime behaviour but never changes once an
    execution has started.
    """

    # ------------------------------------------------------------------
    # Parallel Execution
    # ------------------------------------------------------------------

    parallel_enabled: bool = False
    max_workers: int = 1

    # ------------------------------------------------------------------
    # Retry Policy
    # ------------------------------------------------------------------

    retry_enabled: bool = False
    retry_attempts: int = 0

    # ------------------------------------------------------------------
    # Observability
    # ------------------------------------------------------------------

    tracing_enabled: bool = False
    metrics_enabled: bool = True

    # ------------------------------------------------------------------
    # Runtime Services
    # ------------------------------------------------------------------

    cache_enabled: bool = False
    checkpoint_enabled: bool = False

    # ------------------------------------------------------------------
    # Retry Services
    # ------------------------------------------------------------------

    retry_enabled: bool = True

    max_retry_attempts: int = 3

    retry_delay_seconds: float = 0.0

    retry_exponential_backoff: bool = False

    # ------------------------------------------------------------------
    # Parallel Execution
    # ------------------------------------------------------------------

    parallel_execution: bool = False

    max_workers: int = 4
