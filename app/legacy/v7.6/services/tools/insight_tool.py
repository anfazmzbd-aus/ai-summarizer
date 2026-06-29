import re


def business_insight_tool(text):

    insights = []

    lower = text.lower()

    # Revenue
    revenue = re.search(r"revenue.*?(\d+%)", lower)
    if revenue:
        insights.append(f"Revenue changed by {revenue.group(1)}")
    elif "revenue" in lower:
        insights.append("Revenue movement detected")

    # Profit
    profit_match = re.search(
        r"profit.*?(\d+%)",
        text,
        flags=re.IGNORECASE
    )

    if profit_match:
        insights.append(
            f"Profit changed by {profit_match.group(1)}"
        )
    elif "profit" in lower:
        insights.append(
            "Profit improvement detected"
        )

    # Market
    if "market share" in lower or "market" in lower:
        insights.append("Market expansion detected")

    if (
        "csat" in lower
        or "customer satisfaction" in lower
    ):

        lines = text.splitlines()

        for line in lines:

            lower = line.lower()

            if (
                "csat" in lower
                or
                "customer satisfaction" in lower
            ):

                match = re.search(
                    r"(-?\d+)%?",
                    line
                )

                if match:

                    value = int(
                        match.group(1)
                    )

                    if value > 0:

                        insights.append(
                            f"CSAT increased by {value}%"
                        )

                    elif value < 0:

                        insights.append(
                            f"CSAT decreased by {abs(value)}%"
                        )

    # Generic fallback
    if not insights:
        insights.append("Business activity detected")

    return insights