from app.services.registry.registry import (
    register_agent
)

from app.services.tools.trend_tool import (
    detect_trends
)


@register_agent(
    "trend",
    depends_on=["summary"]
)
def trend_agent(state):

    state["trends"] = detect_trends(
        state["text"]
    )
    print(f"trend_agent: {state.get('trends')}")
    return state