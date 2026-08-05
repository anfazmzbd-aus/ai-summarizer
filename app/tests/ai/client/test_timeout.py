# import asyncio

import pytest

from app.ai import run_with_timeout


@pytest.mark.anyio
async def test_timeout():

    async def work():

        return 123

    result = await run_with_timeout(
        work(),
        1,
    )

    assert result == 123
