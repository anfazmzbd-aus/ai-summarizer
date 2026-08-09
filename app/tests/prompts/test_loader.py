from app.prompts.loader import (
    PromptLoader,
)

from app.prompts.repository import (
    InMemoryPromptRepository,
)


def test_loader():

    repo = InMemoryPromptRepository()

    loader = PromptLoader(repo)

    count = loader.load(())

    assert count == 0
