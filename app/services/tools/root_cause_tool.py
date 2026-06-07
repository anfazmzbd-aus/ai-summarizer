def root_cause_tool(
    insights
):

    causes = []

    for insight in insights:

        if (
            "Market expansion"
            in insight
        ):

            causes.append(
                "Revenue growth appears linked to market expansion."
            )

    return causes