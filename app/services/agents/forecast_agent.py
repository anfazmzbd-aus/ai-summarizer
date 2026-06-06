from app.services.registry.registry import (
    register_agent
)

from app.services.tools.forecast_tool import (
    forecast_tool
)

@register_agent(
    "forecast",
    depends_on=["trend"],
    produces=["forecasts"]
)
def forecast_agent(state):
    forecasts = forecast_tool(state["text"])

    state.setdefault(
        "artifacts",
        {}
    )["forecasts"] = forecasts

    return state