import re
from app.services.registry.registry import (
    register_agent
)
from app.services.tools.action_tool import (
    extract_actions
)

@register_agent(
    "actions",
    depends_on=[] # depends_on["summary"] removed in V7.6 ph6
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