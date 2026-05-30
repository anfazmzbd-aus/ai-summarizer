import re


def extract_actions(text):

    sentences = re.split(r'[.!?]\s+', text)

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

        if any(
            keyword in s.lower()
            for keyword in keywords
        ):
            actions.append(s)

    return list(dict.fromkeys(actions))


def business_insight_tool(text):

    insights = []

    lower_text = text.lower()

    if "revenue" in lower_text:
        insights.append(
            "Revenue trend identified"
        )

    if "%" in text:
        insights.append(
            "Percentage change detected"
        )

    if "profit" in lower_text:
        insights.append(
            "Profit-related information found"
        )

    return insights


def research_finding_tool(text):

    findings = []

    keywords = [
        "research",
        "study",
        "analysis",
        "result"
    ]

    for keyword in keywords:
        if keyword in text.lower():
            findings.append(
                f"Contains {keyword}-related information"
            )

    return findings