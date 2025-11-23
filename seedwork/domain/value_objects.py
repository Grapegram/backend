import uuid
from dataclasses import dataclass
from typing import Any, Protocol, Self

from pydantic import GetCoreSchemaHandler
from returns.pipeline import is_successful
from returns.result import Failure, Result, Success

from seedwork.domain.exceptions import VOValidationException
from seedwork.returns import catch_unwrap


class GenericUUID(uuid.UUID):
    @classmethod
    def next_id(cls):
        return cls(int=uuid.uuid4().int)

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ):
        return handler.generate_schema(uuid.UUID)


class ValueObject(Protocol):
    """
    Base class for value objects
    """

    @classmethod
    def validate(cls, *args, **kwargs) -> Result[None, VOValidationException]:
        """
        Validate the value object creation parameters.
        Should be overridden in subclasses.
        """
        ...

    @classmethod
    def from_raw(cls, *args, **kwargs) -> Self:
        """
        Create a value object from raw data without validation.
        """
        instance = super().__new__(cls)
        instance.__init__(*args, **kwargs)
        return instance

    def __new__(cls, *args, **kwargs) -> Result[Self, VOValidationException]:
        validation_result = catch_unwrap(cls.validate)(*args, **kwargs)
        if not is_successful(validation_result):
            return validation_result

        instance = super().__new__(cls)
        instance.__init__(*args, **kwargs)
        return Success(instance)


@dataclass(frozen=True)
class NotStringError(VOValidationException):
    _msg_fmt = "Value string"


@dataclass(frozen=True)
class EmptyStringError(VOValidationException):
    _msg_fmt = "Value cannot be empty string"


@dataclass(frozen=True)
class StringTooShort(VOValidationException):
    min_length: int
    _msg_fmt = "Valued must be at least {min_length} characters long"


@dataclass(frozen=True)
class StringTooLong(VOValidationException):
    max_length: int
    _msg_fmt = "Value must be at most {max_length} characters long"


class BoundedString(ValueObject):
    """
    A value object for strings with length constraints.
    Subclass this and override min_length and max_length.
    """

    MIN_LENGTH: int = 0
    MAX_LENGTH: int | None = None
    _value: str

    def __init__(self, value: str):
        self._value = value

    @classmethod
    def validate(cls, value: str) -> Result[None, VOValidationException]:
        if not isinstance(value, str):
            return Failure(NotStringError())

        if len(value) == 0 and cls.MIN_LENGTH > 0:
            return Failure(EmptyStringError())

        if len(value) < cls.MIN_LENGTH:
            return Failure(StringTooShort(min_length=cls.MIN_LENGTH))

        if cls.MAX_LENGTH is not None and len(value) > cls.MAX_LENGTH:
            return Failure(StringTooLong(max_length=cls.MAX_LENGTH))

        return Success(None)

    @property
    def value(self) -> str:
        return str(self._value)

    @property
    def length(self) -> int:
        return len(self)

    def __len__(self) -> int:
        return len(self._value)

    def __eq__(self, other) -> bool:
        if isinstance(other, BoundedString):
            return self._value == other._value
        if isinstance(other, str):
            return self._value == other
        return False

    def __hash__(self) -> int:
        return hash(self._value)
