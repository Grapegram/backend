from typing import Protocol


class BusinessRule(Protocol):
    """This is a base class for implementing domain rules"""

    def get_message(self) -> str:
        return self.__doc__

    def is_broken(self) -> bool: ...

    def __str__(self):
        return f"{self.__class__.__name__} {super().__str__()}"
