def root_cause_tool(
    insights,
    trends=None,
    risk=None
):

    trends = trends or []
    risk = risk or []

    causes = []

    text = (
        " ".join(insights)
        + " "
        + " ".join(trends)
        + " "
        + " ".join(risk)
    ).lower()

    has_revenue = (
        "revenue"
        in text
    )

    has_growth = (
        "increase"
        in text
        or "growth"
        in text
    )

    has_market = (
        "market"
        in text
        or "expansion"
        in text
    )

    if (
        has_revenue
        and (
            has_growth
            or has_market
        )
    ):

        causes.append(
            "Revenue growth appears linked to market expansion."
        )

    if (
        "decline"
        in text
        or "decrease"
        in text
    ):
        causes.append(
            "Performance decline may indicate weakening demand."
        )

    if (
        "risk"
        in text
        or "high risk"
        in text
        or "moderate risk"
        in text
    ):
        causes.append(
            "Observed risks may be affecting outcomes."
        )

    if not causes:

        causes.append(
            "No clear root cause identified."
        )

    return list(
        dict.fromkeys(causes)
    )