from app.services.logging.logger import logger
from app.services.context.section_parser import (
    split_sections
)

def semantic_router(
    text,
    intent_info,
    strategy
):
    logger.info(
        f"INPUT STRATEGY: {strategy}"
    )

    sections = split_sections(
        text
    )
    logger.info(
        f"PARSED SECTIONS: {sections}"
    )
    text = text.lower()

    scores = {
        "actions": 0,
        "insights": 0,
        "findings": 0
    }

    reasons = {
        "actions": [],
        "insights": [],
        "findings": [],
        "trends": []
    }

    action_keywords = [
        "should",
        "must",
        "follow up",
        "need to"
    ]

    insight_keywords = [
        "revenue",
        "profit",
        "market",
        "sales",
        "csat",
        "nps",
        "customer satisfaction"
    ]

    finding_keywords = [
        "research",
        "study",
        "analysis"
    ]

    for word in action_keywords:
        if word in text:
            scores["actions"] += 1
            reasons["actions"].append(
                f"{word} detected"
            )

    for word in insight_keywords:
        if word in text:
            scores["insights"] += 1
            reasons["insights"].append(
                f"{word} detected"
            )

    for word in finding_keywords:
        if word in text:
            scores["findings"] += 1
            reasons["findings"].append(
                f"{word} detected"
            )
    

    confidence = {}

    confidence["actions"] = round(
        scores["actions"] / len(action_keywords),
        2
    )

    confidence["insights"] = round(
        scores["insights"] / len(insight_keywords),
        2
    )

    confidence["findings"] = round(
        scores["findings"] / len(finding_keywords),
        2
    )

    if scores["actions"] > 0:
        strategy.append(
            "actions"
        )

    strategy = list(
        dict.fromkeys(strategy)
    )

    # --------------------------------------------------
    # Debug prints
    # --------------------------------------------------
    logger.debug("===semantic_router DEBUG: AGENT GRAPH EXECUTION START===")
    logger.debug(f"PRIMARY INTENT: {intent_info['primary_intent']}")
    logger.debug(f"INTENTS: {intent_info['intents']}")
    logger.debug(f"SELECTED AGENTS: {strategy}")
    logger.debug(f"SCORES: {scores}")
    logger.debug(f"CONFIDENCE: {confidence}")
    logger.debug(f"REASONS: {reasons}")
    logger.debug("===semantic_router DEBUG: AGENT GRAPH EXECUTION END===")
    logger.info(f"SECTIONS: {sections}")

    return {
        "primary_intent": intent_info[
            "primary_intent"
        ],

        "intents": intent_info[
            "intents"
        ],

        "sections": sections,

        "selected_agents": strategy,

        "scores": scores,

        "confidence": confidence,

        "reasons": reasons
    }