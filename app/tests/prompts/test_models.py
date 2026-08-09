from app.prompts.models import (
    PromptDefinition,
    PromptMetadata,
)

from app.prompts.value_objects import (
    PromptId,
    PromptVariable,
    PromptVersion,
)


def create_metadata():

    return PromptMetadata(
        prompt_id=PromptId("summary"),
        version=PromptVersion(
            1,
            0,
            0,
        ),
        description="Summary prompt",
        author="system",
    )


def test_metadata_creation():

    metadata = create_metadata()

    assert metadata.prompt_id.value == "summary"

    assert str(metadata.version) == "1.0.0"


def test_prompt_definition_creation():

    prompt = PromptDefinition.create(
        metadata=create_metadata(),
        system_template=("You summarize documents."),
        user_template=("Summarize {{document}}"),
        variables=(
            PromptVariable(
                name="document",
                description="Source text",
            ),
        ),
    )

    assert prompt.metadata.prompt_id.value == "summary"

    assert len(prompt.variables) == 1


def test_empty_system_template():

    try:
        PromptDefinition.create(
            metadata=create_metadata(),
            system_template="",
            user_template="hello",
        )

    except ValueError:
        assert True

    else:
        assert False


def test_empty_user_template():

    try:
        PromptDefinition.create(
            metadata=create_metadata(),
            system_template="hello",
            user_template="",
        )

    except ValueError:
        assert True

    else:
        assert False
