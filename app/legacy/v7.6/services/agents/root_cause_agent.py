from app.services.registry.registry import register_agent
from app.services.tools.root_cause_tool import root_cause_tool
from app.services.logging.logger import logger

@register_agent(
    "root_cause",
    depends_on=[
        "insights",
        "trend",
        "risk"
    ],
    produces=[
        "root_causes"
    ]
)

def root_cause_agent(state):

    artifacts = state.get(
        "artifacts",
        {}
    )

    context = state.get(
        "context",
        {}
    )

    insights = (
        artifacts.get(
            "insights",
            []
        )
        or context.get(
            "insights",
            []
        )
    )

    trends = (
        artifacts.get(
            "trends",
            []
        )
        or context.get(
            "trends",
            []
        )
    )

    risk = (
        artifacts.get(
            "risk",
            []
        )
        or context.get(
            "risk",
            []
        )
    )

    logger.info(
        f"****ROOT CAUSE INPUT: "
        f"{insights}, "
        f"{trends}, "
        f"{risk}"
    )

    root_causes = root_cause_tool(
        insights,
        trends,
        risk
    )

    state.setdefault(
        "artifacts",
        {}
    )["root_causes"] = root_causes

    return state