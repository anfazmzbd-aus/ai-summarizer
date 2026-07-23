from dataclasses import dataclass


@dataclass(slots=True)
class HookContext:

    runtime_context: object

    state: object
