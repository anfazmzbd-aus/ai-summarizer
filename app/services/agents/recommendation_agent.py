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
    artifacts = state.get(
        "artifacts",
        {}
    )

    recommendations = (
        recommendation_tool(
            artifacts.get(
                "forecasts",
                []
            ),
            artifacts.get(
                "risk",
                []
            )
        )
    )

    state.setdefault(
        "artifacts",
        {}
    )["recommendations"] = recommendations

    return state

