import pytest

from app.prompts.value_objects import (
    PromptId,
    PromptVariable,
    PromptVersion,
)


def test_prompt_id():

    value = PromptId("business_summary")

    assert value.value == "business_summary"


def test_empty_prompt_id():

    with pytest.raises(ValueError):
        PromptId("")


def test_prompt_version():

    version = PromptVersion(
        1,
        2,
        3,
    )

    assert str(version) == "1.2.3"


def test_negative_version():

    with pytest.raises(ValueError):
        PromptVersion(
            -1,
            0,
            0,
        )


def test_prompt_variable():

    variable = PromptVariable(
        name="document",
        description="Input document",
    )

    assert variable.name == "document"
    assert variable.required is True


def test_empty_variable_name():

    with pytest.raises(ValueError):
        PromptVariable(
            name="",
            description="invalid",
        )
