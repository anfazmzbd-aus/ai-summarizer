# Intent Routing — V7.6

Supported intents:

* business_report
* meeting_notes
* research_report
* fallback

Rules:

If no intent exceeds threshold:

primary_intent = fallback

Example:

Input:
John bought 3 apples for $5 each

Output:

primary_intent:
fallback

selected_agents:
summary

Purpose:
Avoid accidental routing into business pipelines.
