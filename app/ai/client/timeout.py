"""
Timeout helper.
"""

from __future__ import annotations

import asyncio


async def run_with_timeout(
    coroutine,
    timeout: float,
):
    return await asyncio.wait_for(
        coroutine,
        timeout,
    )
