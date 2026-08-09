from dataclasses import dataclass, field
from typing import Any


@dataclass
class State:
    """
    Runtime state for a single execution.

    global_context contains execution/business data.

    services contains runtime capabilities made available to agents.
    Keeping services separate from global_context prevents infrastructure
    dependencies from being mixed with execution data.
    """

    global_context: dict[str, Any] = field(default_factory=dict)

    artifacts: dict[str, Any] = field(default_factory=dict)

    node_outputs: dict[str, Any] = field(default_factory=dict)

    services: dict[str, Any] = field(default_factory=dict)
