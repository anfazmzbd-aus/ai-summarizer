import re

def forecast_tool(trends):

    forecasts = []

    for trend in trends:

        match = re.search(
            r"(\d+)%",
            trend
        )

        if match:

            value = match.group(1)

            forecasts.append(
                f"Growth trend of {value}% may continue."
            )

    return forecasts