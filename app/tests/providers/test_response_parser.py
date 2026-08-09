import pytest

from app.providers.response_parser import (
    ResponseParser,
)


def test_response_parser_is_abstract():

    with pytest.raises(TypeError):
        ResponseParser()
