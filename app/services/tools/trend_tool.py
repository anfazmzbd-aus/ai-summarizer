import re


def detect_trends(insights):

    trends = []

    for insight in insights:

        matches = re.findall(
            r"-?\d+%",
            insight
        )

        for match in matches:

            value = int(
                match.replace(
                    "%",
                    ""
                )
            )

            if value >= 0:

                trends.append(
                    f"{value}% increase detected"
                )

            else:

                trends.append(
                    f"{abs(value)}% decrease detected"
                )
    print(f"TREND TOOL Trends: {trends}")
    return trends