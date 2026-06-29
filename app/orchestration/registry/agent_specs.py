from dataclasses import dataclass
from dataclasses import field

from typing import Any
from typing import Set
from typing import Tuple
from typing import Dict


@dataclass(frozen=True)
class AgentSpec:

    # identity

    name: str

    function_name: str

    # execution

    agent: Any

    contract: Any

    # graph

    dependencies: Tuple[
        str,
        ...
    ] = ()

    reads: Set[
        str
    ] = field(
        default_factory=set
    )

    writes: Set[
        str
    ] = field(
        default_factory=set
    )

    # retry

    retryable: bool = True

    timeout_seconds: float = 30

    max_retries: int = 1

    # extension

    metadata: Dict = field(
        default_factory=dict
    )