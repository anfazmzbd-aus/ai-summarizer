from transformers import pipeline
import re


# Load model once at startup
summarizer_model = pipeline(
    "summarization",
    model="facebook/bart-large-cnn"
)


def classify_content(text):

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
        "market",
        "sales"
    ]):
        return "Business Report"

    elif any(word in text_lower for word in [
        "research",
        "study",
        "analysis"
    ]):
        return "Research Article"

    return "General Content"


def extract_action_items(text):

    sentences = re.split(r'[.!?]\s+', text)

    keywords = [
        "should",
        "must",
        "need to",
        "needs to",
        "follow up",
        "action",
        "required",
        "todo",
        "task"
    ]

    actions = []

    for sentence in sentences:

        sentence = sentence.strip()

        if sentence and any(
            keyword in sentence.lower()
            for keyword in keywords
        ):
            actions.append(sentence)

    # remove duplicates while preserving order
    return list(dict.fromkeys(actions))[:5]


def summarize_text(text, summary_length):

    content_type = classify_content(text)

    input_words = len(text.split())

    if len(text.split()) < 60:
        return {
            "content_type": content_type,
            "summary": text,  # avoid over-compression
            "actions": extract_action_items(text)
        }
    
    # dynamic summary sizing
    settings = {
        "short": {
            "max": min(60, input_words),
            "min": min(25, input_words // 3)
        },
        "medium": {
            "max": min(100, input_words),
            "min": min(40, input_words // 3)
        },
        "long": {
            "max": min(150, input_words),
            "min": min(60, input_words // 3)
        }
    }

    config = settings.get(summary_length)

    result = summarizer_model(
        text,
        max_length=config["max"],
        min_length=config["min"],
        do_sample=False,
        truncation=True
    )

    summary = result[0]["summary_text"]

    actions = extract_action_items(text)

    return {
        "content_type": content_type,
        "summary": summary,
        "actions": actions
    }