from app.services.registry.registry import (
    register_agent
)

from app.services.tools.trend_tool import (
    detect_trends
)
from app.services.logging.logger import logger

@register_agent(
    "trend",
    depends_on=["insights"],
    produces=["trends"]
)
def trend_agent(state):
    trends = detect_trends(state["text"])
    
    formatted_trends = []

    for trend in trends:
        if trend["metric"] == "percentage":
            value = trend["value"]

            if value >= 0:
                formatted_trends.append(
                    f"{value}% increase detected"
                )
            else:
                formatted_trends.append(
                    f"{abs(value)}% decrease detected"
                )
    state.setdefault(
        "artifacts",
        {}
    )["trends"] = formatted_trends
    
    logger.info(f"TREND AGENT: {state['artifacts']['trends']}")
    logger.info(f"FORMATTED TREND AGENT: {formatted_trends}")
    return state