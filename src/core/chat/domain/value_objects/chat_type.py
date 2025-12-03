"""
Chat Type Value Object

Defines the type of chat (group or direct).
"""

from enum import Enum


class ChatType(Enum):
    """Enumeration of chat types."""

    GROUP = "group"
    DIRECT = "direct"
