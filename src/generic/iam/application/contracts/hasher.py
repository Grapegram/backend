from typing import Protocol


class HasherService(Protocol):
    def hash(self, plain_text: str) -> str: ...

    def verify(self, plain_text: str, hashed_text: str) -> bool: ...
