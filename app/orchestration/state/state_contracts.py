from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class StateContract:

    input_fields: List[str]

    output_fields: List[str]


DEFAULT_CONTRACT = StateContract(
    input_fields=[
        "global_context",
        "artifacts",
        "node_outputs",
    ],
    output_fields=[]
)   