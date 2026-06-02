from app.services.registry.registry import (
    register_agent
)


@register_agent("trend")
def trend_agent(state):

    state["trends"] = []

    return state