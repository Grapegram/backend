from abc import ABC
from dataclasses import dataclass
from typing import ClassVar


@dataclass
class FormattedError(Exception, ABC):
    """Base class for formatted errors.

    This class provides a flexible way to create custom exceptions with formatted
    error messages. Subclasses should define a `_msg_fmt` string and can specify
    which fields to include in the formatted message using `_formatted_fields`.

    Attributes:
        _msg_fmt: A class variable defining the format string for the error message.
        _formatted_fields: A class variable specifying which fields to include in the
            formatted message. Defaults to ("*",), which includes all fields.
    """

    _msg_fmt: ClassVar[str]
    _formatted_fields: ClassVar[tuple[str]] = ("*",)
    __slots__ = ["_formatted_fields", "_msg_fmt"]

    @property
    def msg(self):
        fields: set[str] = set(self._formatted_fields)

        if "*" in fields:
            fields |= set(self.__dataclass_fields__.keys())
            fields.remove("*")

        return self._msg_fmt.format(**{field: getattr(self, field) for field in fields})

    def __str__(self) -> str:
        return self.msg
