import asyncio
import inspect

from seedwork.application.handlers import Command, Handler, Message, Query, handle


def test_message_subclasses():
    """
    Command and Query should be subclasses/instances of Message.
    Message is a frozen dataclass-based ABC with no fields, so instantiation
    of subclasses should succeed.
    """
    c = Command()
    q = Query()

    assert isinstance(c, Message)
    assert isinstance(q, Message)
    assert type(c) is Command
    assert type(q) is Query


def test_handler_with_async_function_calls_underlying_and_returns_coroutine():
    """
    When a Handler wraps an async function, calling the Handler should
    return a coroutine (which can be awaited/run).
    The wrapped function should receive the positional and keyword args.
    """
    recorded = {}

    async def my_handler(a, b, kw=0):
        recorded["called"] = True
        recorded["args"] = (a, b)
        recorded["kw"] = kw
        return a + b + kw

    h = Handler(handled="marker", handler=my_handler)

    coro = h(1, 2, kw=3)
    # Handler should forward the call to the underlying async function and return a coroutine
    assert inspect.iscoroutine(coro)

    result = asyncio.run(coro)
    assert result == 6
    assert recorded["called"] is True
    assert recorded["args"] == (1, 2)
    assert recorded["kw"] == 3


def test_handle_decorator_creates_handler_and_preserves_handled():
    """
    The `handle` decorator must return a `Handler` instance that wraps the
    original function and preserves the `handled` value on the Handler.
    """

    handled_obj = object()

    @handle(handled_obj)
    async def double(x):
        return x * 2

    # The decorator must return a Handler instance wrapping the original function
    assert isinstance(double, Handler)
    assert double.handled is handled_obj

    result = asyncio.run(double(5))
    assert result == 10


def test_handler_supports_sync_functions_too():
    """
    If the underlying handler is a synchronous function, calling the Handler
    should return the direct result (not a coroutine).
    """

    def plus_one(x):
        return x + 1

    h = Handler(handled="sync", handler=plus_one)
    result = h(2)
    assert result == 3
    assert not inspect.iscoroutine(result)


def test_handler_forwards_args_and_kwargs_for_sync_handlers():
    """
    Ensure positional and keyword arguments are forwarded correctly to sync handlers.
    """

    def echo(*args, **kwargs):
        return {"args": args, "kwargs": kwargs}

    h = Handler(handled="echo", handler=echo)
    out = h(1, 2, a=3, b=4)
    assert out["args"] == (1, 2)
    assert out["kwargs"] == {"a": 3, "b": 4}
