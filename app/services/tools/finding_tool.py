import re
from app.services.logging.logger import logger

def research_finding_tool(text):

    findings = []

    keywords = [
        "research",
        "study",
        "analysis",
        "result"
    ]

    for line in text.splitlines():

        line = line.strip()

        if not line:
            continue
        lower = line.lower()

        if (
            lower == "research report"
        ):
            continue

        if any(
            keyword in lower
            for keyword in keywords
        ):
            findings.append(line)

    logger.info(f"FINDING TOOL OUTPUT: {findings}")
    logger.info(f"FINDING TOOL RETURN: {list(dict.fromkeys(findings))}")
    return list(dict.fromkeys(findings))