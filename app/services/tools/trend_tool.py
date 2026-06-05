import re


def detect_trends(text):

    trends = []

    percent_matches = re.findall(
        r'([+-]?\d+)%',
        text
    )

    for value in percent_matches:

        trends.append(
            {
                "metric": "percentage",
                "value": int(value)
            }
        )
    print(f"trend_tool: {trends}")
    return trends