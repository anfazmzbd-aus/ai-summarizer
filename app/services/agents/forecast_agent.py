from app.services.registry.registry import (
    register_agent
)

from app.services.tools.forecast_tool import (
    forecast_tool
)
from app.services.logging.logger import logger
@register_agent(
    "forecast",
    depends_on=["trend"],
    produces=["forecasts"]
)
def forecast_agent(state):
    trends = (
        state.get(
            "artifacts",
            {}
        ).get(
            "trends",
            []
        )
    )
    print("FORECAST INPUT:", trends)
    logger.info(f"FORECAST INPUT: {trends}")
    forecasts = forecast_tool(
        trends
    )

    state.setdefault(
        "artifacts",
        {}
    )["forecasts"] = forecasts

    return state