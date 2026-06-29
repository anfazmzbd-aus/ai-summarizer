import re


def forecast_tool(trends):

    forecasts = []

    for trend in trends:

        if "increase" in trend.lower():

            value = re.search(
                r"(\d+)",
                trend
            ).group(1)

            forecasts.append(
                f"Growth trend of {value}% may continue."
            )

        elif "decrease" in trend.lower():

            value = re.search(
                r"(\d+)",
                trend
            ).group(1)

            forecasts.append(
                f"Declining trend of {value}% may continue."
            )

    return forecasts