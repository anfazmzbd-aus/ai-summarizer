import re
from app.services.registry.registry import (
    register_agent
)
from app.services.tools.action_tool import (
    extract_actions
)

@register_agent(
    "actions",
    depends_on=["summary"]
)

def actions_agent(state):

    actions = extract_actions(state["text"])

    cleaned = []

    for action in actions:

        action = re.sub(
            r"^[a-zA-Z\s]+:\s*",
            "",
            action,
            flags=re.IGNORECASE
        )

        cleaned.append(action.strip())

    state.setdefault(
        "artifacts",
        {}
    )["actions"] = cleaned
    
    return state