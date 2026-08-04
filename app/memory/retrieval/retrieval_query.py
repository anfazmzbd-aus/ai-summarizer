"""
Retrieval query model.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class RetrievalQuery:

    text: str

    limit: int = 5
