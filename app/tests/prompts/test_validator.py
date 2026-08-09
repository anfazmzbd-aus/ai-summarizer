import pytest

from app.prompts.exceptions import PromptValidationError
from app.prompts.models import PromptDefinition, PromptMetadata
from app.prompts.validator import PromptValidator
from app.prompts.value_objects import (
    PromptId,
    PromptVariable,
    PromptVersion,
)


def prompt():

    return PromptDefinition.create(
        metadata=PromptMetadata(
            prompt_id=PromptId("summary"),
            version=PromptVersion(1, 0, 0),
            description="",
            author="system",
        ),
        system_template="System",
        user_template="{{document}}",
        variables=(
            PromptVariable(
                "document",
                "text",
            ),
        ),
    )


def test_validator_success():

    PromptValidator.validate(
        prompt(),
        {
            "document": "abc",
        },
    )


def test_missing_variable():

    with pytest.raises(PromptValidationError):
        PromptValidator.validate(
            prompt(),
            {},
        )
