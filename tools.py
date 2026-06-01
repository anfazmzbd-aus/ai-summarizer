import re


def extract_actions(text):

    sentences = re.split(
        r'[.!?]\s+|\n+',
        text
    )

    keywords = [
        "should",
        "must",
        "need to",
        "needs to",
        "follow up",
        "action",
        "task"
    ]

    actions = []

    for s in sentences:

        s = s.strip()
        lower = s.lower()

        if (
            "should" in lower
            or "must" in lower
            or "need to" in lower
            or "needs to" in lower
        ):
            s = re.sub(
                r"^[A-Za-z\s]+:\s*",
                "",
                s
            )

            actions.append(s.strip())

    return list(dict.fromkeys(actions))


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

    # Generic fallback
    if not insights:
        insights.append("Business activity detected")

    return insights


def research_finding_tool(text):

    findings = []

    sentences = re.split(
        r"[.!?]\s+",
        text
    )

    keywords = [
        "research",
        "study",
        "analysis",
        "result"
    ]

    for sentence in sentences:

        if any(
            keyword in sentence.lower()
            for keyword in keywords
        ):
            findings.append(
                sentence.strip()
            )

    return list(dict.fromkeys(findings))