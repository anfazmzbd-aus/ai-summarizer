def recommendation_tool(
    forecasts,
    risks
):

    recommendations = []

    if forecasts:

        recommendations.append(
            "Increase investment in growth channels."
        )

    if (
        "High Risk"
        in risks
    ):

        recommendations.append(
            "Develop risk mitigation plans."
        )

    return recommendations