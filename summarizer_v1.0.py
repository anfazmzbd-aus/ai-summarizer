import os
from openai import OpenAI
from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(
    filename="app.log",
    level=logging.INFO
)

#client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"), # Recommended env variable name
)

def summarize_text(text, summary_length="medium"):

    length_instruction = {
        "short": "Summarize in 2-3 sentences.",
        "medium": "Summarize clearly in one paragraph.",
        "long": "Provide a detailed summary with key points."
    }

    prompt = f"""
    {length_instruction.get(summary_length)}

    Text:
    {text}
    """

    logging.info(
        f"Summary request: {summary_length}"
    )

    try:
        response = client.chat.completions.create(
            model="openai/gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional text summarizer."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3
        )

        return response.choices[0].message.content

    except Exception as e:
        logging.error(str(e))
        return f"Error: {str(e)}"