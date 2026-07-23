from dataclasses import dataclass


@dataclass(slots=True)
class CachePolicy:

    enabled: bool = True
    max_entries: int = 5
    ttl_seconds: int = 300
