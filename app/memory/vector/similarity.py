"""
Similarity calculation.
"""

from __future__ import annotations

import math


def cosine_similarity(
    first: list[float],
    second: list[float],
) -> float:

    numerator = sum(a * b for a, b in zip(first, second))

    first_norm = math.sqrt(sum(a * a for a in first))

    second_norm = math.sqrt(sum(b * b for b in second))

    if first_norm == 0 or second_norm == 0:
        return 0.0

    return numerator / (first_norm * second_norm)
