from app.services.registry.registry import register_agent
from app.services.tools.root_cause_tool import root_cause_tool
from app.services.logging.logger import logger

@register_agent(
    "root_cause",
    depends_on=["insights"],
    produces=["root_causes"]
)
def root_cause_agent(state):

    insights = (
        state.get(
            "artifacts",
            {}
        ).get(
            "insights",
            []
        )
    )

    root_causes = (
        root_cause_tool(
            insights
        )
    )

    state.setdefault(
        "artifacts",
        {}
    )["root_causes"] = root_causes
    logger.info(f"ROOT CAUSES: {root_causes}")
    return state