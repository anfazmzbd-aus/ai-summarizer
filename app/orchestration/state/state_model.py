from dataclasses import dataclass
from dataclasses import field
from typing import Dict
from typing import Any


@dataclass
class State:

    global_context: Dict[
        str,
        Any
    ] = field(
        default_factory=dict
    )

    artifacts: Dict[
        str,
        Any
    ] = field(
        default_factory=dict
    )

    node_outputs: Dict[
        str,
        Any
    ] = field(
        default_factory=dict
    )