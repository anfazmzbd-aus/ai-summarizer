from __future__ import annotations

from datetime import datetime
from datetime import timedelta

from .cache_entry import CacheEntry
from .cache_policy import CachePolicy


class ExecutionCache:
    """
    In-memory execution cache.

    Responsibilities:
    - store execution results
    - enforce TTL expiration
    - enforce maximum entries
    - provide cache lifecycle operations
    """

    def __init__(
        self,
        policy: CachePolicy | None = None,
    ):

        self._policy = policy or CachePolicy()

        self._entries: dict[str, CacheEntry] = {}

    def get(
        self,
        key: str,
    ):

        if not self._policy.enabled:
            return None

        entry = self._entries.get(key)

        if entry is None:
            return None

        expires = entry.created_at + timedelta(
            seconds=self._policy.ttl_seconds,
        )

        if datetime.utcnow() >= expires:
            self._entries.pop(
                key,
                None,
            )

            return None

        return entry.value

    def put(
        self,
        key: str,
        value: object,
    ):

        if not self._policy.enabled:
            return

        self._entries[key] = CacheEntry(
            key=key,
            value=value,
            created_at=datetime.utcnow(),
        )

        self._evict_if_needed()

    def delete(
        self,
        key: str,
    ):

        self._entries.pop(
            key,
            None,
        )

    def clear(self):

        self._entries.clear()

    def contains(
        self,
        key: str,
    ) -> bool:

        return self.get(key) is not None

    @property
    def size(
        self,
    ) -> int:

        return len(self)

    def _evict_if_needed(
        self,
    ):

        while len(self._entries) > self._policy.max_entries:

            oldest_key = min(
                self._entries,
                key=lambda k: self._entries[k].created_at,
            )

            del self._entries[oldest_key]

    def __contains__(
        self,
        key: str,
    ):

        return self.contains(key)

    def __len__(
        self,
    ):

        expired = []

        now = datetime.utcnow()

        for key, entry in self._entries.items():

            expires = entry.created_at + timedelta(
                seconds=self._policy.ttl_seconds,
            )

            if now >= expires:
                expired.append(key)

        for key in expired:
            self._entries.pop(
                key,
                None,
            )

        return len(self._entries)
