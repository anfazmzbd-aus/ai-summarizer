"""
AI Summarizer V8.0 Distributed Runtime

Worker lifecycle events.
"""

from __future__ import annotations

from enum import Enum


class WorkerEventType(str, Enum):
    """
    Worker runtime events.
    """

    STARTED = "worker_started"

    REGISTERED = "worker_registered"

    TASK_RECEIVED = "task_received"

    TASK_STARTED = "task_started"

    TASK_COMPLETED = "task_completed"

    TASK_FAILED = "task_failed"

    HEARTBEAT_SENT = "heartbeat_sent"

    STOPPING = "worker_stopping"

    STOPPED = "worker_stopped"
