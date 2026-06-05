def recommendation_tool(text):

    recs = []

    lower = text.lower()

    if "market" in lower:

        recs.append(
            "Increase investment in growth channels."
        )

    if "revenue" in lower:

        recs.append(
            "Monitor sustainability of revenue growth."
        )

    return recs