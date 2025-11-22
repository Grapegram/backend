from asyncio import iscoroutinefunction
from contextlib import suppress
from functools import partial, wraps
from types import MethodType

from _stories.execute import coroutine, function
from _stories.step import _Step
from stories import I, State


class Interrupt(Exception):
    """Story execution interruption exception."""


def catch_interrupt(func):
    if iscoroutinefunction(func):

        @wraps(func)
        async def wrapper(*args, **kwargs):
            with suppress(Interrupt):
                return await func(*args, **kwargs)
    else:

        @wraps(func)
        def wrapper(*args, **kwargs):
            with suppress(Interrupt):
                return func(*args, **kwargs)

    return wrapper


class _Executor:
    def __init__(self, steps):
        self.steps = steps

    def __get__(self, instance, klass):
        if instance is None:
            return self
        first_step = getattr(instance, self.steps[0])
        if isinstance(first_step, MethodType):
            step = first_step.__func__
        else:
            step = first_step.__call__.func
        if iscoroutinefunction(step):
            func = coroutine._execute
        else:
            func = function._execute

        return partial(catch_interrupt(func), self.steps, instance)


class _StoryType(type):
    def __prepare__(class_name, bases):
        return {"I": _Step()}

    def __new__(cls, class_name, bases, namespace):
        steps = namespace.pop("I").steps
        if not bases:
            return type.__new__(cls, class_name, bases, namespace)
        namespace["__call__"] = _Executor(steps)
        return type.__new__(cls, class_name, bases, namespace)


class Story(metaclass=_StoryType):
    """Business process specification.

    Use sentences from business domain to express its steps.

    """


__all__ = ["Story", "Interrupt", "I", "State"]
