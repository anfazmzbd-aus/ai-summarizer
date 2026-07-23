from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class Timeout:
    """
    Runtime timeout configuration.
    """

    seconds: float
