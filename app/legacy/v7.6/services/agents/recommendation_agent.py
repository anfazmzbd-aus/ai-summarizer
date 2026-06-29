from app.services.registry.registry import (
    register_agent
)

from app.services.tools.recommendation_tool import (
    recommendation_tool
)

@register_agent(
    "recommendation",
    depends_on=[
        "forecast",
        "risk"
    ],
    produces=[
        "recommendations"
    ]
)

def recommendation_agent(state):

    context = state.get("context", {})
    artifacts = state.get("artifacts", {})

    recommendations = recommendation_tool(
        forecasts=(
            artifacts.get("forecasts", [])
            or context.get("forecast", [])
        ),
        risk=(
            artifacts.get("risk", [])
            or context.get("risk", [])
        ),
        trends=context.get("trends", []),
        insights=context.get("insights", [])
    )

    state.setdefault(
        "artifacts",
        {}
    )["recommendations"] = recommendations

    return state

