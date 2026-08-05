from app.ai import PromptTemplate


def test_prompt_template():

    template = PromptTemplate(
        name="summary",
        version="1.0",
        template="Summarize: {text}",
    )

    assert template.name == "summary"
    assert template.version == "1.0"
