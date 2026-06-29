def recommendation_tool(
    forecasts=None,
    risk=None,
    trends=None,
    insights=None
):

    forecasts = forecasts or []
    risk = risk or []
    trends = trends or []
    insights = insights or []

    recommendations = []

    forecast_text = (
        " ".join(forecasts)
    ).lower()

    risk_text = (
        " ".join(risk)
    ).lower()

    trend_text = (
        " ".join(trends)
    ).lower()

    insight_text = (
        " ".join(insights)
    ).lower()

    if (
        "growth"
        in forecast_text
        or "increase"
        in trend_text
    ):
        recommendations.append(
            "Increase investment in growth channels."
        )

    if (
        "declining"
        in forecast_text
        or "decrease"
        in trend_text
    ):
        recommendations.append(
            "Investigate causes of decline and apply corrective actions."
        )

    if (
        "risk"
        in risk_text
        or "high"
        in risk_text
    ):
        recommendations.append(
            "Develop risk mitigation plans."
        )

    if (
        "customer satisfaction"
        in insight_text
        or "csat"
        in insight_text
    ):
        recommendations.append(
            "Monitor customer feedback and improve retention."
        )

    if not recommendations:

        recommendations.append(
            "No recommendations generated."
        )

    return list(
        dict.fromkeys(
            recommendations
        )
    )