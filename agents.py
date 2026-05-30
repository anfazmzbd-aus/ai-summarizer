import re
from summarizer import summarizer_model
from memory import fetch_recent_summaries
from tools import (
    extract_actions,
    business_insight_tool,
    research_finding_tool
)

# ----------------------------
# A. CONTENT CLASSIFER AGENT
# ----------------------------
def content_classifier_agent(text):

    text_lower = text.lower()

    if any(word in text_lower for word in [
        "meeting",
        "agenda",
        "follow up",
        "action item"
    ]):
        return "Meeting Notes"

    elif any(word in text_lower for word in [
        "revenue",
        "profit",
        "sales",
        "market"
    ]):
        return "Business Report"

    elif any(word in text_lower for word in [
        "research",
        "study",
        "analysis"
    ]):
        return "Research Article"

    return "General Content"

# ----------------------------
# 1. PLANNER AGENT
# ----------------------------
def planner_agent(text):

    content_type = content_classifier_agent(text)

    plan = {
        "content_type": content_type,
        "tools": []
    }

    if content_type == "Meeting Notes":
        plan["tools"] = [
            "summary",
            "actions"
        ]

    elif content_type == "Business Report":
        plan["tools"] = [
            "summary",
            "business_insights"
        ]

    elif content_type == "Research Article":
        plan["tools"] = [
            "summary",
            "research_findings"
        ]

    else:
        plan["tools"] = [
            "summary"
        ]

    return plan


# ----------------------------
# 2. SUMMARIZER AGENT
# ----------------------------
def summarizer_agent(text, summary_length):

    input_words = len(text.split())

    if len(text.split()) < 40:
        return text
    
    # safer dynamic bounds (token-safe approximation)
    if summary_length == "short":
        max_len = min(80, max(40, input_words))
        min_len = 20

    elif summary_length == "medium":
        max_len = min(120, max(60, input_words))
        min_len = 30

    else:
        max_len = min(160, max(80, input_words))
        min_len = 40

    result = summarizer_model(
        text,
        max_length=max_len,
        min_length=min_len,
        do_sample=False,
        truncation=True
    )

    summary = result[0]["summary_text"]

    return summary.strip()


# ----------------------------
# 3. ACTION EXTRACTOR AGENT
# ----------------------------
def action_agent(text):

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

        s_clean = s.strip()

        if not s_clean:
            continue

        if any(k in s_clean.lower() for k in keywords):

            # remove prefixes like "Meeting agenda:"
            s_clean = re.sub(r"^[A-Za-z\s]+:\s*", "", s_clean)

            actions.append(s_clean)

    return list(dict.fromkeys(actions))[:5]

# ----------------------------
# 4. ORCHESTRATOR
# ----------------------------
def run_agents(text, summary_length="medium"):

    plan = planner_agent(text)

    summary = summarizer_agent(
        text,
        summary_length
    )

    result = {
        "content_type":
            plan["content_type"],

        "summary":
            summary,

        "plan":
            plan
    }

    if "actions" in plan["tools"]:
        result["actions"] = (
            extract_actions(text)
        )

    if "business_insights" in plan["tools"]:
        result["insights"] = (
            business_insight_tool(text)
        )

    if "research_findings" in plan["tools"]:
        result["findings"] = (
            research_finding_tool(text)
        )

    return result