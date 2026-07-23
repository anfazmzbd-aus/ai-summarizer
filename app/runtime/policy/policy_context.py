from dataclasses import dataclass


@dataclass
class PolicyContext:
    """
    Context used when resolving execution policies.
    """

    execution_id: str

    node: str | None = None

    agent_type: str | None = None
