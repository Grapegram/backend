import uuid
from typing import Any, Protocol, Self

from pydantic import GetCoreSchemaHandler
from returns.pipeline import is_successful
from returns.result import Result, Success


class GenericUUID(uuid.UUID):
    @classmethod
    def next_id(cls):
        return cls(int=uuid.uuid4().int)

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: GetCoreSchemaHandler):
        return handler.generate_schema(uuid.UUID)


class ValueObject(Protocol):
    """
    Base class for value objects
    """

    @classmethod
    def validate(cls, *args, **kwargs) -> Result[Self, ValueError]:
        """
        Validate the value object creation parameters.
        Should be overridden in subclasses.
        """
        ...

    def __new__(cls, *args, **kwargs) -> Result[Self, ValueError]:
        validation_result = cls.validate(*args, **kwargs)
        if not is_successful(validation_result):
            return validation_result
        return Success(super().__new__(cls))
