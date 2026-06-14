from app.services.logging.logger import logger

def classify_intent(text):

    text = text.lower()

    business_score = 0
    meeting_score = 0
    research_score = 0

    business_words = [
        "revenue",
        "profit",
        "market",
        "sales",
        "%"
    ]

    meeting_words = [
        "meeting",
        "agenda",
        "should",
        "must",
        "follow up"
    ]

    research_words = [
        "research",
        "study",
        "analysis",
        "result"
    ]

    for word in business_words:
        if word in text:
            business_score += 1

    for word in meeting_words:
        if word in text:
            meeting_score += 1

    for word in research_words:
        if word in text:
            research_score += 1

    scores = {
        "business_report": business_score,
        "meeting_notes": meeting_score,
        "research_report": research_score
    }

    primary_intent = max(scores, key=scores.get)

    detected_intents = []
    for intent_name, score in scores.items():
        if score > 0:
            detected_intents.append(intent_name)

    logger.info(
        f"****INTENT SCORES: {scores}"
    )

    logger.info(
        f"****PRIMARY INTENT: {primary_intent}"
    )

    logger.info(
        f"****SELECTED INTENTS: {detected_intents}"
    )

    return {
        "primary_intent": primary_intent,
        "intents": detected_intents,
        "scores": scores
    }

