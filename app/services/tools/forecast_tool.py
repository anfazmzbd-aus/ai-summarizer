import re

def forecast_tool(text):

    percentages = re.findall(
        r"(\d+)%",
        text
    )

    forecasts = []

    for p in percentages:

        if int(p) > 10:

            forecasts.append(
                f"Growth trend of {p}% may continue."
            )

    return forecasts