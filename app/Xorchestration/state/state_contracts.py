from dataclasses import dataclass, field
from typing import Callable
from typing import Dict
from typing import Any
from typing import Tuple


Validator = Callable[[Any], None]


# -------------------------
# State Requirements
# -------------------------

@dataclass(frozen=True)
class StateRequirement:

    required_artifacts: Tuple[
        str,
        ...
    ] = ()

    required_outputs: Tuple[
        str,
        ...
    ] = ()

    required_context_keys: Tuple[
        str,
        ...
    ] = ()


# -------------------------
# State Contract
# -------------------------

@dataclass(frozen=True)
class StateContract:

    input_validator: Validator

    output_validator: Validator

    requirements: StateRequirement = field(
        default_factory=StateRequirement
    )

    metadata: Dict[
        str,
        Any
    ] = field(
        default_factory=dict
    )

    def validate_input(
        self,
        data: Any,
    ) -> None:

        self.input_validator(
            data
        )

    def validate_output(
        self,
        data: Any,
    ) -> None:

        self.output_validator(
            data
        )


# -------------------------
# Default Validators
# -------------------------

def allow_any(
    data: Any,
) -> None:

    return


def require_dict(
    data: Any,
) -> None:

    if not isinstance(
        data,
        dict,
    ):

        raise ValueError(
            "Expected dict output"
        )


DEFAULT_CONTRACT = (
    StateContract(
        input_validator=allow_any,
        output_validator=require_dict,
    )
)