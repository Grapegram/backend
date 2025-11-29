from classes import typeclass

from .aggregates import Chat, Message


@typeclass
def to_message(instance) -> Message:
    """Convert various representations to a Message aggregate in Chat context."""


@typeclass
def to_chat(instance) -> Chat:
    """Convert various representations to a Chat aggregate in Chat context."""
