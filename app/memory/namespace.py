"""
Memory namespaces.
"""

from enum import Enum


class MemoryNamespace(str, Enum):

    GLOBAL = "global"

    TENANT = "tenant"

    SESSION = "session"

    EXECUTION = "execution"

    AGENT = "agent"
