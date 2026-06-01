def planner_agent(text: str) -> dict:

    text_lower = text.lower()

    is_meeting = any(
        keyword in text_lower
        for keyword in ["agenda", "meeting", "discuss", "minutes"]
    )

    needs_actions = is_meeting

    needs_insights = True

    needs_findings = len(text) > 200

    return {
        "is_meeting": is_meeting,
        "needs_summary": True,
        "needs_actions": needs_actions,
        "needs_insights": needs_insights,
        "needs_findings": needs_findings
    }