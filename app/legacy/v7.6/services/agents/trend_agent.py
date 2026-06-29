from app.services.registry.registry import register_agent
from app.services.tools.trend_tool import detect_trends
from app.services.logging.logger import logger

@register_agent(
    "trend",
    depends_on=["insights"],
    produces=["trends"]
)

def trend_agent(state):
    insights = (
        state.get(
            "artifacts",
            {}
        ).get(
            "insights",
            []
        )
    )

    trends = detect_trends(
        insights
    )
    
    state.setdefault(
        "artifacts",
        {}
    )["trends"] = trends
    
    logger.info(f"****TREND AGENT: {state['artifacts']['trends']}")
    logger.info(f"****FORMATTED TREND AGENT: {trends}")
    return state