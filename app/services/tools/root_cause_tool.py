def root_cause_tool(text):

    causes = []

    lower = text.lower()

    if (
        "revenue" in lower
        and "market" in lower
    ):
        causes.append(
            "Revenue growth appears linked to market expansion."
        )

    if (
        "profit" in lower
        and "sales" in lower
    ):
        causes.append(
            "Profit growth may be driven by increased sales."
        )

    return causes