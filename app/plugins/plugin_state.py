"""
Plugin lifecycle states.
"""

from enum import Enum


class PluginState(str, Enum):

    REGISTERED = "registered"

    INITIALIZED = "initialized"

    ACTIVE = "active"

    STOPPED = "stopped"

    FAILED = "failed"
